import streamlit as st
import bcrypt, sqlite3
from datetime import datetime

DEFAULT_FDC = "6P4rVEgRsNBnS8bAYqlq2DEDqiaf72txvmATH05g"

def hash_pw(pw:str)->bytes:
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt())

def check_pw(pw:str, h:bytes)->bool:
    try: return bcrypt.checkpw(pw.encode(), h)
    except Exception: return False

def login_register_ui(conn):
    st.sidebar.header("Carioca 🌴")
    with st.form("login_form", clear_on_submit=False):
        u = st.text_input("Username", key="login_user")
        p = st.text_input("Password", type="password", key="login_pw")
        remember = st.checkbox("Remember Me", value=True)
        submitted = st.form_submit_button("Login")
    st.markdown("""
    <script>
    const btn = window.parent.document.querySelector('form[data-testid="stForm"] button');
    window.addEventListener('keydown', (e)=>{ if(e.key==='Enter'){ if(btn) btn.click(); }});
    </script>
    """, unsafe_allow_html=True)

    if submitted:
        row = conn.execute("SELECT pw_hash, lang FROM users WHERE username=?", (u,)).fetchone()
        if row and check_pw(p, row[0]):
            st.session_state["user"] = u
            st.session_state["remember"] = remember
            st.rerun()
        else:
            st.error("Invalid credentials")

    st.divider()
    st.subheader("Register")
    ru = st.text_input("Username *", key="ru")
    rp = st.text_input("Password *", type="password", key="rp")
    if st.button("Register"):
        if not ru or not rp:
            st.warning("Fill required fields")
        else:
            try:
                conn.execute("""INSERT INTO users(username, pw_hash, lang, fdc_key, created_at)
                                VALUES(?,?,?,?,?)""",
                             (ru, hash_pw(rp), "en", DEFAULT_FDC, datetime.utcnow().isoformat()))
                conn.commit()
                st.success("Registered. Please log in.")
            except sqlite3.IntegrityError:
                st.error("Username already exists")
