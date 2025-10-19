import streamlit as st, pandas as pd, plotly.express as px
from datetime import date

def render(conn, user_row):
    u = st.session_state["user"]
    st.subheader("Progress")
    c1,c2 = st.columns([2,1])
    with c1:
        w = st.number_input("Weight (kg)", 30.0, 300.0, step=0.1)
        waist = st.number_input("Waist (cm)", 40.0, 200.0, step=0.5)
    with c2:
        if st.button("Add"):
            conn.execute("INSERT INTO progress_logs(username, dt, weight, waist) VALUES(?,?,?,?)", (u, date.today().isoformat(), float(w), float(waist)))
            conn.commit(); st.success("Saved")

    wdf = pd.read_sql_query("SELECT id, dt, weight, waist FROM progress_logs WHERE username=? ORDER BY dt", conn, params=(u,))
    if not wdf.empty:
        fig = px.line(wdf, x="dt", y=["weight","waist"], markers=True, title="Weight & Waist Trend")
        fig.update_xaxes(title="Zaman / Timeline")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(wdf, use_container_width=True)
        del_id = st.number_input("Delete row id", min_value=0, step=1)
        if st.button("Delete") and del_id:
            conn.execute("DELETE FROM progress_logs WHERE rowid=? AND username=?", (int(del_id), u))
            conn.commit(); st.success("Deleted — refresh the page")
    else:
        st.info("No data yet")
