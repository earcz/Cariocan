# app.py — Carioca v28
import streamlit as st
import sqlite3
from datetime import datetime

# ---- doğru importlar ----
try:
    from core.theme import render_header
    from core.auth import login_register_ui
except ModuleNotFoundError:
    # Streamlit çalışma dizini değişirse güvenli yol
    import sys, os
    sys.path.append(os.path.dirname(__file__))
    from core.theme import render_header
    from core.auth import login_register_ui

# ---- SAYFA AYARLARI ----
st.set_page_config(page_title="Carioca", page_icon="🌴", layout="wide")

# ---- DB ----
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

# ---- SESSION ----
st.session_state.setdefault("user", None)
st.session_state.setdefault("lang", "en")

# ---- DİL SEÇİMİ (sidebar) ----
st.sidebar.header("🌐 Language / Dil")
lang_choice = st.sidebar.radio("Select language", ["English", "Türkçe"],
                               index=0 if st.session_state["lang"] == "en" else 1)
st.session_state["lang"] = "en" if lang_choice == "English" else "tr"

# ---- LOGIN YOKSA ----
if not st.session_state["user"]:
    login_register_ui(conn)   # core.auth içinden
    st.stop()

# ---- KULLANICIYI ÇEK ----
row = conn.execute("SELECT username, avatar, lang FROM users WHERE username=?",
                   (st.session_state["user"],)).fetchone()
if not row:
    st.error("User not found.")
    st.stop()

username, avatar_data, lang = row
render_header(user_name=username, avatar_data=avatar_data)

# ---- LOGOUT (sidebar alt) ----
st.sidebar.markdown("---")
if st.sidebar.button("🚪 Logout"):
    keep_lang = st.session_state.get("lang", "en")
    st.session_state.clear()
    st.session_state["lang"] = keep_lang
    st.rerun()

# ---- SEKMELER ----
from features import profile, nutrition, progress, workout, reminders, summary

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
