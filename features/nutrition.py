import streamlit as st, pandas as pd, plotly.graph_objects as go
from datetime import date
from core.api_food import off_search, fdc_search, macros_from_grams
from core.calc import mifflin_st_jeor, activity_factor, macro_split

def render(conn, user_row):
    u, lang, theme, avatar, email, fdc_key, plan_type, meal_structure, age, sex, height_cm, weight_kg, bodyfat, birthdate, activity, target_weight, training_days, fasting, full_name, waist_cm = user_row
    st.subheader("Log Food")
    picked_date = st.date_input("Date", value=date.today(), format="DD.MM.YYYY", key="nut_date")
    meal_sel = st.selectbox("Meal", ["1st Main","2nd Main","3rd Main","1st Snack","2nd Snack","3rd Snack"])
    colA, colB, colC = st.columns([3,1,1])
    with colA: q = st.text_input("Search Food")
    with colB: grams = st.number_input("Amount (g)", 1, 2000, 100)
    with colC: lang_pick = st.radio("Language", ["en","tr"], horizontal=True, key="food_lang")

    df = pd.DataFrame()
    if q:
        df_off = off_search(q, "tr" if lang_pick=="tr" else "en")
        df_fdc = fdc_search(q, fdc_key) if fdc_key else pd.DataFrame()
        frames = [x for x in [df_fdc, df_off] if not x.empty]
        if frames: df = pd.concat(frames, ignore_index=True)
    show_cols = ["source","name","brand","kcal_100g","protein_100g","carbs_100g","fat_100g","sugars_100g","fiber_100g","sodium_100g","salt_100g"]
    st.dataframe(df[show_cols] if not df.empty else df, use_container_width=True)
    if df.empty and q: st.warning("No results — try simpler words")

    if not df.empty:
        sel_idx = st.selectbox("Select", list(range(len(df))), format_func=lambda i: f"{df.iloc[i]['name']} ({df.iloc[i]['brand']}) [{df.iloc[i]['source']}]")
        if st.button("Add"):
            rowf = df.iloc[int(sel_idx)].to_dict(); vals = macros_from_grams(rowf, grams)
            conn.execute("""INSERT INTO food_logs(username, dt, meal, food_name, grams, kcal, protein, carbs, fat, sugars, fiber, sodium, salt) 
                            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", 
                         (u, picked_date.isoformat(), meal_sel, rowf['name'], grams, vals["kcal"], vals["protein"], vals["carbs"], vals["fat"], vals["sugars"], vals["fiber"], vals["sodium"], vals["salt"]))
            conn.commit(); st.success("Added")

    weekday = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"][picked_date.weekday()]
    st.subheader(f"{picked_date.strftime('%d.%m.%Y')} {weekday}")
    logs = pd.read_sql_query("""SELECT meal, food_name, grams, kcal, protein, carbs, fat 
                                FROM food_logs WHERE username=? AND dt=? ORDER BY meal""", conn, params=(u, picked_date.isoformat()))
    st.dataframe(logs, use_container_width=True)

    bmr = mifflin_st_jeor(sex, weight_kg, height_cm, age)
    is_workout = st.toggle("Workout day?", value=(picked_date.weekday() in [0,2,4]))
    base_tdee = bmr*activity_factor(activity) if is_workout else bmr*1.35
    target_cal = round(base_tdee*0.75)
    tp, tc, tf = macro_split(target_cal, workout=is_workout, weight=weight_kg)
    tot = logs[["kcal","protein","carbs","fat"]].sum() if not logs.empty else pd.Series({"kcal":0,"protein":0,"carbs":0,"fat":0})

    fig = go.Figure()
    fig.add_trace(go.Bar(x=["Calories"], y=[min(tot["kcal"], target_cal)], name="Taken"))
    over_cal = max(0, tot["kcal"]-target_cal)
    if over_cal>0: fig.add_trace(go.Bar(x=["Calories"], y=[over_cal], name="Over", marker_color="red"))
    fig.add_trace(go.Bar(x=["Protein (g)"], y=[min(tot["protein"], tp)], name="Taken"))
    over_p = max(0, tot["protein"]-tp)
    if over_p>0: fig.add_trace(go.Bar(x=["Protein (g)"], y=[over_p], marker_color="red", showlegend=False))
    fig.add_trace(go.Bar(x=["Carbs (g)"], y=[min(tot["carbs"], tc)], name="Taken"))
    over_c = max(0, tot["carbs"]-tc)
    if over_c>0: fig.add_trace(go.Bar(x=["Carbs (g)"], y=[over_c], marker_color="red", showlegend=False))
    fig.update_layout(barmode="stack", yaxis=dict(range=[0, max(target_cal, tp, tc)+100]))
    st.plotly_chart(fig, use_container_width=True)

    deficit = (target_cal - float(tot["kcal"]))
    if deficit>0: st.success(f"Daily deficit: {int(deficit)} kcal → ~{round(deficit/7700,3)} kg fat")
    else: st.warning(f"Exceeded by {int(-deficit)} kcal")
