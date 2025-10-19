import streamlit as st
from datetime import datetime
import sqlite3, json
from core.theme import render_header
from features import profile, nutrition, progress, workout, reminders, summary

# ---- SAYFA AYARLARI ----
st.set_page_config(page_title="Carioca", page_icon="🌴", layout="wide")

# ---- DATABASE ----
def get_conn():
    conn = sqlite3.connect("carioca_v28.db", check_same_thread=False)
    conn.execute("""CREATE TABLE IF NOT EXISTS users(
        username TEXT PRIMARY KEY,
        pw_hash BLOB,
        lang TEXT DEFAULT 'en',
        avatar TEXT,
        email TEXT,
        fdc_key TEXT,
        plan_type TEXT,
        meal_structure TEXT,
        age INT,
        sex TEXT,
        height_cm REAL,
        weight_kg REAL,
        waist_cm REAL,
        bodyfat REAL,
        activity TEXT,
        fasting TEXT,
        created_at TEXT
    )""")
    conn.commit()
    return conn

conn = get_conn()

# ---- SESSION & LOGIN DURUMU ----
if "user" not in st.session_state:
    st.session_state["user"] = None
if "lang" not in st.session_state:
    st.session_state["lang"] = "en"

# ---- DİL SEÇİMİ ----
st.sidebar.header("🌐 Language / Dil")
lang_choice = st.sidebar.radio("Select language", ["English", "Türkçe"],
                               index=0 if st.session_state["lang"] == "en" else 1)

st.session_state["lang"] = "en" if lang_choice == "English" else "tr"

# ---- LOGIN DURUMU YOKSA ----
if not st.session_state["user"]:
    from features.auth import login_register_ui
    login_register_ui(conn)
    st.stop()

# ---- KULLANICIYI ÇEK ----
row = conn.execute("""SELECT username, avatar, lang FROM users WHERE username=?""",
                   (st.session_state["user"],)).fetchone()
if not row:
    st.error("User not found in database.")
    st.stop()

username, avatar_data, lang = row
render_header(user_name=username, avatar_data=avatar_data)

# ---- SIDEBAR LOGOUT ----
st.sidebar.markdown("---")
if st.sidebar.button("🚪 Logout"):
    user_lang = st.session_state["lang"]
    st.session_state.clear()
    st.session_state["lang"] = user_lang
    st.success("Logged out successfully.")
    st.rerun()

# ---- SEKMELER ----
tabs = st.tabs(["Profile", "Nutrition", "Workout", "Progress", "Reminders", "Summary"])

with tabs[0]:
    profile.render(conn, username)

with tabs[1]:
    nutrition.render(conn, username)

with tabs[2]:
    workout.render(conn, username)

with tabs[3]:
    progress.render(conn, username)

with tabs[4]:
    reminders.render(conn, username)

with tabs[5]:
    summary.render(conn, username)
