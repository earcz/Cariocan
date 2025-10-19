import streamlit as st
from pathlib import Path
import base64

# ---- Genel Ayarlar ----
ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"
RIO_IMG_PATH = ASSETS_DIR / "Rio.png"

def load_rio_base64():
    """Rio görselini base64 formatında döndürür."""
    if not RIO_IMG_PATH.exists():
        return ""
    with open(RIO_IMG_PATH, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

# ---- CSS Teması ----
def apply_minimal_theme():
    """Uygulamanın genel minimal temasını uygular."""
    css = """
    <style>
    html, body, [class*="stAppViewContainer"], .main, .block-container {
        background-color: #f8fafc !important;
        color: #222;
        font-family: 'Inter', sans-serif;
    }

    /* Ana container */
    .block-container {
        padding: 1.5rem 2rem;
        border-radius: 18px;
        background-color: rgba(255,255,255,0.85);
        backdrop-filter: blur(6px);
        box-shadow: 0 4px 16px rgba(0,0,0,0.05);
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 1px solid #e5e7eb;
        padding: 1rem 0.8rem !important;
    }

    /* Butonlar */
    div.stButton > button {
        background: linear-gradient(90deg, #00c6ff 0%, #0072ff 100%) !important;
        color: white !important;
        border-radius: 12px !important;
        border: none !important;
        font-weight: 600 !important;
        transition: 0.2s;
    }
    div.stButton > button:hover {
        background: linear-gradient(90deg, #0072ff 0%, #00c6ff 100%) !important;
        transform: scale(1.02);
    }

    /* Header alanı */
    .carioca-header {
        position: relative;
        width: 100%;
        height: 160px;
        background: rgba(255,255,255,0.85);
        border-radius: 16px;
        overflow: hidden;
        margin-bottom: 1.5rem;
    }
    .carioca-header::before {
        content: "";
        position: absolute;
        inset: 0;
        background-image: url("data:image/png;base64,{rio_img}");
        background-size: cover;
        background-position: center;
        opacity: 0.25;
        z-index: 0;
    }
    .carioca-header h1 {
        position: relative;
        z-index: 2;
        color: #111827;
        font-size: 2.6rem;
        font-weight: 800;
        margin: 1.2rem 0 0 2rem;
    }
    .carioca-header .user-img {
        position: absolute;
        top: 1.2rem;
        right: 1.5rem;
        width: 80px;
        height: 80px;
        border-radius: 50%;
        border: 3px solid white;
        box-shadow: 0 4px 10px rgba(0,0,0,0.15);
        object-fit: cover;
    }
    @media (max-width: 768px) {
        .carioca-header {
            height: 120px;
        }
        .carioca-header h1 {
            font-size: 2rem;
            margin-left: 1rem;
        }
        .carioca-header .user-img {
            width: 60px;
            height: 60px;
        }
    }
    </style>
    """.replace("{rio_img}", load_rio_base64())
    st.markdown(css, unsafe_allow_html=True)

# ---- Header Render ----
def render_header(user_name: str = "Carioca", avatar_data=None):
    """Sayfanın üst kısmındaki başlık ve profil fotoğrafı alanı."""
    apply_minimal_theme()
    st.markdown(f"""
    <div class="carioca-header">
        <h1>{user_name}</h1>
        {'<img src="'+avatar_data+'" class="user-img"/>' if avatar_data else ''}
    </div>
    """, unsafe_allow_html=True)
