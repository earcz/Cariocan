import streamlit as st
from core import theme
from features import profile, nutrition, workout, progress, summary
import sqlite3

# ---- PAGE CONFIG ----
st.set_page_config(page_title="Carioca", page_icon="🌴", layout="wide")

# ---- THEME ----
theme.apply_minimal_theme()

# ---- DB CONNECTION ----
@st.cache_resource
def get_conn():
    conn = sqlite3.connect("carioca_v28.db", check_same_thread=False)
    return conn

conn = get_conn()

# ---- SESSION PERSISTENCE ----
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "username" not in st.session_state:
    st.session_state["username"] = None
if "avatar" not in st.session_state:
    st.session_state["avatar"] = None
if "language" not in st.session_state:
    st.session_state["language"] = "en"

# ---- SIDEBAR ----
with st.sidebar:
    st.markdown("### 🌍 Language / Dil")
    lang = st.radio("", ["English", "Türkçe"], horizontal=True,
                    index=0 if st.session_state["language"] == "en" else 1)
    st.session_state["language"] = "en" if lang == "English" else "tr"

    st.markdown("---")
    if st.button("🚪 Logout"):
        st.session_state["logged_in"] = False
        st.session_state["username"] = None
        st.rerun()

# ---- LOGIN MOCK (örnek) ----
if not st.session_state["logged_in"]:
    st.markdown("### 🔑 Login Simulation")
    user_input = st.text_input("Username", "")
    if st.button("Login"):
        if user_input:
            st.session_state["logged_in"] = True
            st.session_state["username"] = user_input
            st.session_state["avatar"] = None
            st.rerun()
    st.stop()

# ---- HEADER ----
theme.render_header(st.session_state["username"], st.session_state["avatar"])

# ---- TABS ----
tabs = st.tabs([
    "Profile", "Nutrition", "Workout", "Progress", "Summary"
])

# ---- FEATURE PAGES ----
with tabs[0]:
    profile.render(conn, st.session_state["username"], st.session_state["language"])

with tabs[1]:
    nutrition.render(conn, st.session_state["username"], st.session_state["language"])

with tabs[2]:
    workout.render(conn, st.session_state["username"], st.session_state["language"])

with tabs[3]:
    progress.render(conn, st.session_state["username"], st.session_state["language"])

with tabs[4]:
    summary.render(conn, st.session_state["username"], st.session_state["language"])
