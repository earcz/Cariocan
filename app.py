import streamlit as st
from core import db, theme, auth
from features import profile, deficit, nutrition, workout, progress, reminders, summary

st.set_page_config(page_title="Carioca", page_icon="🌴", layout="wide")
theme.apply_minimal_theme()
conn = db.get_conn()

if "user" not in st.session_state:
    auth.login_register_ui(conn)
    st.stop()

user = st.session_state["user"]
row = conn.execute("""SELECT username, lang, theme, avatar, email, fdc_key, plan_type, meal_structure, age, sex, height_cm, weight_kg,
                             bodyfat, birthdate, activity, target_weight, training_days, fasting, full_name, waist_cm
                      FROM users WHERE username=?""", (user,)).fetchone()

st.session_state.setdefault("theme", row[2] or "tropical")
theme.header("Carioca", subtitle=row[18] or "Personalized plan engine • Theme toggle • OFF + FDC", avatar_b64=row[3], theme=st.session_state["theme"])

if st.sidebar.button("Logout"):
    st.session_state.clear(); st.rerun()
picked_theme = st.sidebar.radio("Theme", ["tropical","minimal"], index=0 if st.session_state["theme"]=="tropical" else 1)
st.session_state["theme"] = picked_theme

tabs = st.tabs(["Profile", "Deficit Calc", "Nutrition", "Workout", "Progress", "Reminders", "Summary"])
with tabs[0]: profile.render(conn, row)
with tabs[1]: deficit.render(row)
with tabs[2]: nutrition.render(conn, row)
with tabs[3]: workout.render(conn, row)
with tabs[4]: progress.render(conn, row)
with tabs[5]: reminders.render()
with tabs[6]: summary.render(conn, row)
