import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import date
from core.api_food import off_search, fdc_search, macros_from_grams
from core.calc import mifflin_st_jeor, activity_factor, macro_split

def render(conn, user_row):
    u, lang, theme, avatar, email, fdc_key, plan_type, meal_structure, age, sex, height_cm, weight_kg, bodyfat, birthdate, activity, target_weight, training_days, fasting, full_name, waist_cm = user_row

    # ---- FOOD INPUT ----
    st.subheader("Log Food")
    picked_date = st.date_input("Date", value=date.today(), format="DD.MM.YYYY", key="nut_date")
    meal_sel = st.selectbox("Meal", ["1st Main","2nd Main","3rd Main","1st Snack","2nd Snack","3rd Snack"])

    colA, colB, colC = st.columns([3,1,1])
    with colA:
        q = st.text_input("Search Food")
    with colB:
        grams = st.number_input("Amount (g)", 1, 2000, 100)
    with colC:
        lang_pick = st.radio("Language", ["English","Türkçe"], horizontal=True, key="food_lang")

    # ---- SEARCH ----
    df = pd.DataFrame()
    if q:
        try:
            df_off = off_search(q, "tr" if lang_pick == "Türkçe" else "en")
        except Exception as e:
            st.warning(f"OFF search failed: {e}")
            df_off = pd.DataFrame()
        try:
            df_fdc = fdc_search(q, fdc_key) if fdc_key else pd.DataFrame()
        except Exception as e:
            st.warning(f"FDC search failed: {e}")
            df_fdc = pd.DataFrame()

        frames = [x for x in [df_fdc, df_off] if not x.empty]
        if frames:
            df = pd.concat(frames, ignore_index=True)

    # ---- SHOW RESULTS ----
    show_cols = ["source","name","brand","kcal_100g","protein_100g","carbs_100g","fat_100g","sugars_100g","fiber_100g","sodium_100g","salt_100g"]
    st.dataframe(df[show_cols] if not df.empty else df, use_container_width=True)
    if df.empty and q:
        st.warning("No results — try simpler keywords (e.g. 'egg', 'rice').")

    # ---- ADD TO LOG ----
    if not df.empty:
        sel_idx = st.selectbox(
            "Select food",
            list(range(len(df))),
            format_func=lambda i: f"{df.iloc[i]['name']} ({df.iloc[i]['brand']}) [{df.iloc[i]['source']}]"
        )
        if st.button("Add to log"):
            try:
                rowf = df.iloc[int(sel_idx)].to_dict()
                vals = macros_from_grams(rowf, grams)
                conn.execute("""
                    INSERT INTO food_logs(username, dt, meal, food_name, grams, kcal, protein, carbs, fat, sugars, fiber, sodium, salt)
                    VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """, (
                    u, picked_date.isoformat(), meal_sel, rowf.get('name','Unknown'), grams,
                    vals.get("kcal",0), vals.get("protein",0), vals.get("carbs",0), vals.get("fat",0),
                    vals.get("sugars",0), vals.get("fiber",0), vals.get("sodium",0), vals.get("salt",0)
                ))
                conn.commit()
                st.success(f"✅ Added {grams} g of {rowf.get('name','food')} to log.")
            except Exception as e:
                st.error(f"Insert error: {e}")

    # ---- DAILY LOG ----
    weekday = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"][picked_date.weekday()]
    st.subheader(f"{picked_date.strftime('%d.%m.%Y')} ({weekday})")

    logs = pd.read_sql_query("""
        SELECT meal, food_name, grams, kcal, protein, carbs, fat 
        FROM food_logs WHERE username=? AND dt=? ORDER BY meal
    """, conn, params=(u, picked_date.isoformat()))

    if not logs.empty:
        st.dataframe(logs, use_container_width=True)
    else:
        st.info("No foods logged yet for this date.")

    # ---- CALCULATIONS ----
    bmr = mifflin_st_jeor(sex, weight_kg, height_cm, age)
    is_workout = st.toggle("Workout day?", value=(picked_date.weekday() in [0,2,4]))
    base_tdee = bmr * activity_factor(activity) if is_workout else bmr * 1.35
    target_cal = round(base_tdee * 0.75)
    tp, tc, tf = macro_split(target_cal, workout=is_workout, weight=weight_kg)

    tot = logs[["kcal","protein","carbs","fat"]].sum() if not logs.empty else pd.Series({"kcal":0,"protein":0,"carbs":0,"fat":0})

    # ---- ADVANCED GRAPH (Calories + 3 Macros) ----
    fig = go.Figure()

    # LEFT AXIS → Calories
    y1_max = max(2500, tot["kcal"] * 1.1, target_cal * 1.1, 5000)
    fig.add_trace(go.Bar(
        x=["Calories"], y=[tot["kcal"]],
        name="Calories", marker_color="#0072ff", yaxis="y1"
    ))
    if tot["kcal"] > target_cal:
        fig.add_trace(go.Bar(
            x=["Calories"], y=[tot["kcal"]-target_cal],
            name="Over Cal", marker_color="red", yaxis="y1"
        ))

    # RIGHT AXIS → Macros (Protein, Carbs, Fat)
    y2_max = max(200, tot["protein"], tot["carbs"], tot["fat"], tp, tc, tf) * 1.2
    fig.add_trace(go.Bar(
        x=["Protein"], y=[tot["protein"]],
        name="Protein (g)", marker_color="#22c55e", yaxis="y2"
    ))
    fig.add_trace(go.Bar(
        x=["Carbs"], y=[tot["carbs"]],
        name="Carbs (g)", marker_color="#f59e0b", yaxis="y2"
    ))
    fig.add_trace(go.Bar(
        x=["Fat"], y=[tot["fat"]],
        name="Fat (g)", marker_color="#ef4444", yaxis="y2"
    ))

    fig.update_layout(
        title="Daily Intake vs Goal",
        barmode="group",
        yaxis=dict(title="Calories (kcal)", range=[0, y1_max]),
        yaxis2=dict(title="Macros (g)", overlaying="y", side="right", range=[0, y2_max]),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
        height=420,
        margin=dict(t=60,b=60)
    )
    st.plotly_chart(fig, use_container_width=True)

    # ---- DEFICIT ----
    deficit = target_cal - float(tot["kcal"])
    if deficit > 0:
        st.success(f"📉 Deficit: {int(deficit)} kcal → ~{round(deficit/7700,3)} kg fat")
    else:
        st.warning(f"🔥 Surplus: +{abs(int(deficit))} kcal over target")
