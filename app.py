# app.py — Carioca v28.3 (persistent session + lang toggle + header subtitle)
import streamlit as st
import sqlite3

try:
    from core.theme import render_header
    from core.auth import login_register_ui
except ModuleNotFoundError:
    import sys, os
    sys.path.append(os.path.dirname(__file__))
    from core.theme import render_header
    from core.auth import login_register_ui

st.set_page_config(page_title="Carioca", page_icon="🌴", layout="wide")

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
    safe_cols = {
        "birthdate": "TEXT",
        "target_weight": "REAL",
        "training_days": "INT",
        "full_name": "TEXT"
    }
    for col, typ in safe_cols.items():
        try: conn.execute(f"ALTER TABLE users ADD COLUMN {col} {typ}")
        except: pass
    conn.commit()
    return conn

conn = get_conn()

# ---- SESSION & URL PARAMS (kalıcı oturum) ----
params = st.experimental_get_query_params()
st.session_state.setdefault("user", None)
st.session_state.setdefault("lang", params.get("lang", ["en"])[0])

# URL'de kullanıcı varsa otomatik oturum
if not st.session_state["user"] and "u" in params:
    st.session_state["user"] = params["u"][0]

# ---- DİL SEÇİMİ (sidebar) ----
st.sidebar.header("🌐 Language / Dil")
lang_choice = st.sidebar.radio(
    "Select language",
    ["English", "Türkçe"],
    index=0 if st.session_state["lang"] == "en" else 1
)
new_lang = "en" if lang_choice == "English" else "tr"
if new_lang != st.session_state["lang"]:
    st.session_state["lang"] = new_lang
    # kullanıcı girişliyse DB'ye yaz ve URL param güncelle
    if st.session_state.get("user"):
        conn.execute("UPDATE users SET lang=? WHERE username=?", (new_lang, st.session_state["user"]))
        conn.commit()
        st.experimental_set_query_params(u=st.session_state["user"], lang=new_lang)
    st.rerun()

# ---- LOGIN YOKSA ----
if not st.session_state["user"]:
    login_register_ui(conn)
    st.stop()

# ---- KULLANICIYI ÇEK (subtitle için full_name da alınır) ----
row = conn.execute("""
    SELECT
      username, lang, avatar, email, fdc_key, plan_type, meal_structure, age, sex, height_cm,
      weight_kg, bodyfat, birthdate, activity, target_weight, training_days, fasting, full_name, waist_cm
    FROM users WHERE username=?
""", (st.session_state["user"],)).fetchone()

if not row:
    st.error("User not found.")
    st.stop()

username = row[0]
full_name = row[17] or ""
avatar_data = row[2]

# URL paramlarını sabitle (yenilemede oturum kalsın)
st.experimental_set_query_params(u=username, lang=st.session_state["lang"])

# Header: Carioca + Full Name (subtitle)
render_header(app_title="Carioca", full_name=full_name, avatar_data=avatar_data)

# ---- LOGOUT (sidebar alt) ----
st.sidebar.markdown("---")
if st.sidebar.button("🚪 Logout"):
    keep_lang = st.session_state.get("lang", "en")
    st.session_state.clear()
    # URL paramlarını temizle
    st.experimental_set_query_params(lang=keep_lang)
    st.session_state["lang"] = keep_lang
    st.rerun()

# ---- SEKMELER (TR/EN başlıklar) ----
tabs_tr = ["Profil", "Beslenme", "Antrenman", "İlerleme", "Hatırlatıcılar", "Özet"]
tabs_en = ["Profile", "Nutrition", "Workout", "Progress", "Reminders", "Summary"]
labels = tabs_tr if st.session_state["lang"] == "tr" else tabs_en

from features import profile, nutrition, progress, workout, reminders, summary

tabs = st.tabs(labels)

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
