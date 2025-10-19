# features/summary.py — resilient version (auto-fix legacy schemas)
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import date, timedelta
from core.calc import mifflin_st_jeor, activity_factor

def _ensure_table_and_columns(conn, table_name: str, create_sql: str, required_cols: dict[str, str]):
    """Tablo yoksa oluştur; varsa PRAGMA ile kolonları kontrol edip eksikleri ekle."""
    conn.execute(create_sql)
    # mevcut kolonları oku
    cur = conn.execute(f"PRAGMA table_info({table_name})")
    existing = {row[1] for row in cur.fetchall()}  # name sütunu
    # eksik kolonları ekle
    for col, coltype in required_cols.items():
        if col not in existing:
            try:
                conn.execute(f"ALTER TABLE {table_name} ADD COLUMN {col} {coltype}")
            except Exception:
                # aynı anda başka istek gelip eklemiş olabilir; sessiz geç
                pass
    conn.commit()

def render(conn, user_row):
    # --- Tablo & kolon güvencesi (eski DB'lerde hatayı keser) ---
    _ensure_table_and_columns(
        conn,
        "food_logs",
        """
        CREATE TABLE IF NOT EXISTS food_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            dt TEXT,
            meal TEXT,
            food_name TEXT,
            grams REAL,
            kcal REAL,
            protein REAL,
            carbs REAL,
            fat REAL,
            sugars REAL,
            fiber REAL,
            sodium REAL,
            salt REAL
        )
        """,
        required_cols={
            "username": "TEXT", "dt": "TEXT", "kcal": "REAL",
            "protein": "REAL", "carbs": "REAL", "fat": "REAL"
        }
    )
    _ensure_table_and_columns(
        conn,
        "workout_logs",
        """
        CREATE TABLE IF NOT EXISTS workout_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            dt TEXT,
            exercise TEXT,
            duration REAL,
            calories REAL
        )
        """,
        required_cols={"username": "TEXT", "dt": "TEXT", "calories": "REAL"}
    )

    # --- Kullanıcı bilgileri ---
    (
        u, lang, avatar, email, fdc_key, plan_type, meal_structure,
        age, sex, height_cm, weight_kg, bodyfat, birthdate,
        activity, target_weight, training_days, fasting,
        full_name, waist_cm,
    ) = user_row

    st.subheader("Summary")

    picked_date = st.date_input("Summary Date", value=date.today(), format="DD.MM.YYYY", key="sum_date")
    range_sel = st.selectbox("Range", ["1 Week", "1 Month", "6 Months", "Custom"])

    if range_sel == "1 Week":
        start, end = picked_date - timedelta(days=7), picked_date
    elif range_sel == "1 Month":
        start, end = picked_date - timedelta(days=30), picked_date
    elif range_sel == "6 Months":
        start, end = picked_date - timedelta(days=182), picked_date
    else:
        c1, c2 = st.columns(2)
        with c1:
            start = st.date_input("Start", value=picked_date - timedelta(days=7))
        with c2:
            end = st.date_input("End", value=picked_date)

    # --- Verileri oku (hata durumunda teşhis çıktısı ver) ---
    try:
        nut = pd.read_sql_query(
            """
            SELECT dt,
                   SUM(kcal)    AS kcal,
                   SUM(protein) AS protein,
                   SUM(carbs)   AS carbs
            FROM food_logs
            WHERE username=? AND dt BETWEEN ? AND ?
            GROUP BY dt
            ORDER BY dt
            """,
            conn,
            params=(u, start.isoformat(), end.isoformat()),
        )
    except Exception as e:
        st.error("Food logs query failed.")
        # Teşhis için mevcut kolonları göster
        cols = conn.execute("PRAGMA table_info(food_logs)").fetchall()
        st.caption("food_logs columns: " + ", ".join([c[1] for c in cols]))
        raise

    try:
        wrk = pd.read_sql_query(
            """
            SELECT dt,
                   COALESCE(SUM(calories), 0) AS kcal
            FROM workout_logs
            WHERE username=? AND dt BETWEEN ? AND ?
            GROUP BY dt
            ORDER BY dt
            """,
            conn,
            params=(u, start.isoformat(), end.isoformat()),
        )
    except Exception as e:
        st.error("Workout logs query failed.")
        cols = conn.execute("PRAGMA table_info(workout_logs)").fetchall()
        st.caption("workout_logs columns: " + ", ".join([c[1] for c in cols]))
        raise

    df = pd.merge(nut, wrk, on="dt", how="left", suffixes=("_eat", "_burn")).fillna(0)
    if df.empty:
        st.info("No data in the selected range.")
        return

    # --- Hedef ve net açık hesapları ---
    bmr = mifflin_st_jeor(sex, weight_kg, height_cm, age)

    def target_for(dt):
        is_w = pd.to_datetime(dt).weekday() in [0, 2, 4]
        base = bmr * activity_factor(activity) if is_w else bmr * 1.35
        return round(base * 0.75)

    df["target"] = df["dt"].apply(target_for)
    df["net_def"] = (df["target"] - df["kcal_eat"]) + df["kcal_burn"]
    df["fat_est"] = df["net_def"].apply(lambda x: x / 7700 if x > 0 else 0)

    # --- Grafik ---
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df["dt"], y=df["net_def"], name="Net Deficit (kcal)"))
    fig.add_trace(
        go.Scatter(
            x=df["dt"], y=df["fat_est"].cumsum(), name="Cum. Fat (kg)", yaxis="y2", mode="lines+markers"
        )
    )
    fig.update_layout(
        yaxis=dict(title="kcal"),
        yaxis2=dict(title="kg", overlaying="y", side="right"),
        margin=dict(l=10, r=10, t=10, b=10),
    )
    st.plotly_chart(fig, use_container_width=True)
