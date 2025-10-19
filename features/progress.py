# features/progress.py
import streamlit as st
import pandas as pd
from datetime import date

TABLE = "progress_logs"

def _ensure_table(conn):
    conn.execute(f"""
    CREATE TABLE IF NOT EXISTS {TABLE}(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        dt TEXT,
        weight REAL,
        waist REAL
    )
    """)
    conn.commit()

def render(conn, username: str):
    _ensure_table(conn)

    st.subheader("Progress")

    # --- Girdi alanları
    c1, c2, c3 = st.columns([1,1,1])
    with c1:
        dt = st.date_input("Date", value=date.today(), format="DD.MM.YYYY", key="prog_date")
    with c2:
        weight = st.number_input("Weight (kg)", min_value=30.0, max_value=300.0, value=80.0, step=0.1, key="prog_weight")
    with c3:
        waist = st.number_input("Waist (cm)", min_value=40.0, max_value=200.0, value=90.0, step=0.5, key="prog_waist")

    if st.button("Add / Update"):
        # aynı güne kayıt varsa update, yoksa insert
        existing = conn.execute(
            f"SELECT id FROM {TABLE} WHERE username=? AND dt=?",
            (username, dt.isoformat())
        ).fetchone()
        if existing:
            conn.execute(
                f"UPDATE {TABLE} SET weight=?, waist=? WHERE id=?",
                (float(weight), float(waist), int(existing[0]))
            )
        else:
            conn.execute(
                f"INSERT INTO {TABLE}(username, dt, weight, waist) VALUES(?,?,?,?)",
                (username, dt.isoformat(), float(weight), float(waist))
            )
        conn.commit()
        st.success("Saved")

    st.divider()

    # --- Kayıtları getir
    try:
        wdf = pd.read_sql_query(
            f"SELECT id, dt, weight, waist FROM {TABLE} WHERE username=? ORDER BY dt",
            conn, params=(username,)
        )
    except Exception as e:
        st.error("Could not read progress logs.")
        st.stop()

    if wdf.empty:
        st.info("No progress yet.")
        return

    # Tarih formatı
    wdf["dt"] = pd.to_datetime(wdf["dt"])

    # Görüntüleme
    st.dataframe(
        wdf.rename(columns={"dt":"Date","weight":"Weight (kg)","waist":"Waist (cm)"}),
        use_container_width=True
    )

    # Silme
    with st.expander("Delete an entry"):
        del_id = st.number_input("Row ID to delete", min_value=0, step=1)
        if st.button("Delete") and del_id:
            conn.execute(f"DELETE FROM {TABLE} WHERE id=? AND username=?", (int(del_id), username))
            conn.commit()
            st.success("Deleted")
            st.experimental_rerun()

    # Grafik (aynı eksende iki seri)
    import plotly.graph_objects as go
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=wdf["dt"], y=wdf["weight"], mode="lines+markers", name="Weight (kg)"))
    fig.add_trace(go.Scatter(x=wdf["dt"], y=wdf["waist"], mode="lines+markers", name="Waist (cm)"))
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Value",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0)
    )
    st.plotly_chart(fig, use_container_width=True)
