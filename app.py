# app.py — Carioca v28 (stable)
import streamlit as st

# Core modules
from core import db, auth, theme

# Feature pages (sekme içerikleri)
from features import profile, nutrition, workout, progress, summary

# -------------------------------
# Page config
# -------------------------------
st.set_page_config(page_title="Carioca", page_icon="🌴", layout="wide")

# Minimal tema (tropik toggle yok)
theme.apply_minimal_theme()

# -------------------------------
# DB connection (persist)
# -------------------------------
@st.cache_resource
def _conn():
    return db.get_conn()

conn = _conn()

# -------------------------------
# Session defaults (persist)
# -------------------------------
ss = st.session_state
ss.setdefault("user", None)           # username (string)
ss.setdefault("avatar", None)         # base64 data-uri string
ss.setdefault("language", "en")       # "en" | "tr"

# -------------------------------
# Sidebar: Dil seçimi + Logout
# -------------------------------
with st.sidebar:
    st.markdown("### 🌍 Language / Dil")
    lang_label = "English" if ss["language"] == "en" else "Türkçe"
    lang_pick = st.radio(
        label="",
        options=["English", "Türkçe"],
        index=0 if ss["language"] == "en" else 1,
        horizontal=True,
    )
    ss["language"] = "en" if lang_pick == "English" else "tr"

    st.markdown("---")
    if st.button("🚪 Logout"):
        # Yalnızca auth ile ilgili anahtarları temizle
        for k in ["user", "avatar"]:
            if k in ss: del ss[k]
        st.rerun()

# -------------------------------
# Auth: Login/Register UI
# -------------------------------
# Eğer kullanıcı yoksa, auth modülü login/register ekranını gösterir ve burada durur
if not ss.get("user"):
    auth.login_register_ui(conn)   # bu fonksiyon kendi içinde formu çizer
    st.stop()                      # login olana kadar devam etme

username = ss["user"]
avatar_data = ss.get("avatar")

# -------------------------------
# Header (Rio.png arkaplan + sağ üstte avatar)
# -------------------------------
# İsim/başlık: profile modulü kullanıcının ad/soyadını saklıyorsa oradan okunabilir;
# yoksa kullanıcı adı gösterilir.
display_name = username
try:
    # Varsa readonly şekilde isim/soyad çek
    urow = db.get_user_row(conn, username)  # core/db.py içinde küçük yardımcı fonksiyon olduğunu varsayar
    if urow:
        full_name = (urow.get("full_name") or "").strip()
        if full_name:
            display_name = full_name
        # avatar’ı profilde güncellediyse session’a yansıt
        if urow.get("avatar"):
            ss["avatar"] = urow["avatar"]
            avatar_data = ss["avatar"]
except Exception:
    pass

theme.render_header(display_name, avatar_data)

# -------------------------------
# Tabs
# -------------------------------
tabs = st.tabs([
    "Profile" if ss["language"] == "en" else "Profil",
    "Nutrition" if ss["language"] == "en" else "Beslenme",
    "Workout" if ss["language"] == "en" else "Antrenman",
    "Progress" if ss["language"] == "en" else "İlerleme",
    "Summary" if ss["language"] == "en" else "Özet",
])

with tabs[0]:
    profile.render(conn, username, ss["language"])

with tabs[1]:
    nutrition.render(conn, username, ss["language"])

with tabs[2]:
    workout.render(conn, username, ss["language"])

with tabs[3]:
    progress.render(conn, username, ss["language"])

with tabs[4]:
    summary.render(conn, username, ss["language"])
