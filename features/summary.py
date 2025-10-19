# features/summary.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import date, timedelta
from core.calc import mifflin_st_jeor, activity_factor

def render(conn, user_row):
    # app.py'deki SELECT sırasına birebir uyumlu unpack
    (
        u,              # username
        lang,
        avatar,
        email,
        fdc_key,
        plan_type,
        meal_structure,
        age,
        sex,
        height_cm,
        weight_kg,
        bodyfat,
        birthdate,
        activity,
        target_weight,
        training_days,
        fasting,
        full_name,
        waist_cm,
    ) = user_row

    st.subheader("Summary")

    picked_date = st.date_input(
        "Summary Date",
        value=date.today(),
        format="DD.MM.YYYY",
        key="sum_date"
    )

    range_sel = st.selectbox("Range", ["1 Week", "1 Month", "6 Months", "Custom"])
    if range_sel == "1 Week":
        start = picked_date - timedelta(days=7)
        end = picked_date
    elif range_sel == "1 Month":
        start = picked_date - timedelta(days=30)
        end = picked_date
    elif range_sel == "6 Months":
        start = picked_date - timedelta(days=182)
        end = picked_date
    else:
        c1, c2 = st.columns(2)
        with c1:
            start = st.date_input("Start", value=picked_date - timedelta(days=7), key="sum_start")
        with c2:
            end = st.date_input("End", value=picked_date, key="sum_end")

    # Beslenme ve antrenman toplamlarını gün bazında çek
    nut = pd.read_sql_query(
        """
        SELECT dt, SUM(kcal)  AS kcal, SUM(protein) AS protein, SUM(carbs) AS carbs
        FROM food_logs
        WHERE username=? AND dt BETWEEN ? AND ?
        GROUP BY dt
        ORDER BY dt
        """,
        conn,
        params=(u, start.isoformat(), end.isoformat()),
    )

    wrk = pd.read_sql_query(
        """
        SELECT dt, SUM(calories) AS kcal
        FROM workout_logs
        WHERE username=? AND dt BETWEEN ? AND ?
        GROUP BY dt
        ORDER BY dt
        """,
        conn,
        params=(u, start.isoformat(), end.isoformat()),
    )

    # Gün bazında tek tablo
    df = pd.merge(nut, wrk, on="dt", how="left", suffixes=("_eat", "_burn")).fillna(0)

    if df.empty:
        st.info("No data in the selected range.")
        return

    # Hedef kalori (güne göre workout/rest varsayımı ile)
    bmr = mifflin_st_jeor(sex, weight_kg, height_cm, age)

    def target_for(dt_str: str) -> int:
        is_workout = pd.to_datetime(dt_str).weekday() in [0, 2, 4]  # Mon/Wed/Fri
        base = bmr * activity_factor(activity) if is_workout else bmr * 1.35
        return int(round(base * 0.75))

    df["target"] = df["dt"].apply(target_for)
    df["net_def"] = (df["target"] - df["kcal_eat"]) + df["kcal_burn"]
    df["fat_est"] = df["net_def"].apply(lambda x: x / 7700 if x > 0 else 0)

    # Grafik: Net açık (sol eksen) + Kümülatif yağ tahmini (sağ eksen)
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df["dt"], y=df["net_def"], name="Net Deficit (kcal)"))
    fig.add_trace(
        go.Scatter(
            x=df["dt"],
            y=df["fat_est"].cumsum(),
            name="Cum. Fat (kg)",
            yaxis="y2",
            mode="lines+markers",
        )
    )
    fig.update_layout(
        barmode="group",
        yaxis=dict(title="kcal"),
        yaxis2=dict(
            overlaying="y",
            side="right",
            title="kg",
            showgrid=False,
        ),
        margin=dict(l=20, r=20, t=10, b=10),
    )
    st.plotly_chart(fig, use_container_width=True)
