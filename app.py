# app.py — Carioca v28.2
import streamlit as st
import sqlite3
from datetime import datetime

# ---- doğru importlar ----
try:
    from core.theme import render_header
    from core.auth import login_register_ui
except ModuleNotFoundError:
    import sys, os
    sys.path.append(os.path.dirname(__file__))
    from core.theme import render_header
    from core.auth import login_register_ui

# ---- SAYFA AYARLARI ----
st.set_page_config(page_title="Carioca", page_icon="🌴", layout="wide")

# ---- DB ----
def get_conn():
    conn = sqlite3.connect("carioca_v28.db", check_same_thread=False)
    # Temel tablo (bazı kolonları bilerek minimum bırakıyoruz; aşağıda güvenli ALTER ile ekleyeceğiz)
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
    # ---- Eksik olabilecek kolonları güvenli şekilde ekle ----
    safe_cols = {
        "birthdate": "TEXT",
        "target_weight": "REAL",
        "training_days": "INT",
        "full_name": "TEXT"
    }
    for col, typ in safe_cols.items():
        try:
            conn.execute(f"ALTER TABLE users ADD COLUMN {col} {typ}")
        except Exception:
            pass
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
    login_register_ui(conn)
    st.stop()

# ---- KULLANICIYI ÇEK (profile.render ile birebir sırada) ----
row = conn.execute("""
    SELECT
      username,       -- 0 (u)
      lang,           -- 1 (lang)
      avatar,         -- 2 (avatar)
      email,          -- 3 (email)
      fdc_key,        -- 4 (fdc_key)
      plan_type,      -- 5 (plan_type)
      meal_structure, -- 6 (meal_structure)
      age,            -- 7 (age)
      sex,            -- 8 (sex)
      height_cm,      -- 9 (height_cm)
      weight_kg,      --10 (weight_kg)
      bodyfat,        --11 (bodyfat)
      birthdate,      --12 (birthdate)
      activity,       --13 (activity)
      target_weight,  --14 (target_weight)
      training_days,  --15 (training_days)
      fasting,        --16 (fasting)
      full_name,      --17 (full_name)
      waist_cm        --18 (waist_cm)
    FROM users
    WHERE username=?
""", (st.session_state["user"],)).fetchone()

if not row:
    st.error("User not found.")
    st.stop()

username = row[0]
avatar_data = row[2]
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
    profile.render(conn, row)

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
