import streamlit as st
from pathlib import Path
import base64

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"
RIO_IMG_PATH = ASSETS_DIR / "Rio.png"

def _load_rio_base64():
    if not RIO_IMG_PATH.exists():
        return ""
    with open(RIO_IMG_PATH, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def apply_minimal_theme():
    css = """
    <style>
    html, body, [class*="stAppViewContainer"], .main, .block-container {
        background-color: #f8fafc !important;
        color: #222;
        font-family: 'Inter', system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
    }

    /* ---- Header hizalama düzeltmesi ---- */
    header[data-testid="stHeader"] {
        z-index: 0 !important;  /* Streamlit toolbar çakışmasını engeller */
    }
    div[data-testid="stAppViewContainer"] > .main {
        padding-top: 1.5rem !important;  /* toolbar ile header arasında boşluk */
    }
    .block-container {
        padding-top: 0.5rem !important;
    }

    section[data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 1px solid #e5e7eb;
        padding: 1rem 0.8rem !important;
    }

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

    /* ---- Carioca Header ---- */
    .carioca-header {
        position: relative;
        width: 100%;
        height: 180px;
        background: rgba(255,255,255,0.92);
        border-radius: 16px;
        overflow: hidden;
        margin: 2.5rem 0 1.5rem 0; /* 🔹 Üst boşluk artırıldı */
        border: 1px solid #e5e7eb;
    }

    .carioca-header::before {
        content: "";
        position: absolute;
        inset: 0;
        background-image: url("data:image/png;base64,{rio_img}");
        background-size: cover;
        background-position: center;
        opacity: 0.22;
        z-index: 0;
    }

    .carioca-header .title {
        position: relative;
        z-index: 2;
        color: #111827;
        font-size: 2.4rem;
        font-weight: 800;
        margin: 1.2rem 0 0 2rem;
        line-height: 1.1;
    }

    .carioca-header .subtitle {
        position: relative;
        z-index: 2;
        color: #374151;
        font-size: 1rem;
        font-weight: 600;
        margin: 0.4rem 0 0 2rem;
        opacity: 0.9;
    }

    .carioca-header .user-img {
        position: absolute;
        top: 1.7rem;
        right: 1.4rem;
        width: 120px;
        height: 120px;
        border-radius: 12px;
        border: 3px solid white;
        box-shadow: 0 4px 10px rgba(0,0,0,0.12);
        object-fit: cover;
        z-index: 2;
        background: #fff;
    }

    @media (max-width: 768px) {
        .carioca-header { height: 140px; margin-top: 1.2rem; }
        .carioca-header .title { font-size: 2rem; margin-left: 1rem; }
        .carioca-header .subtitle { margin-left: 1rem; }
        .carioca-header .user-img { width: 120px; height: 120px; top: 1rem; }
    }
    </style>
    """.replace("{rio_img}", _load_rio_base64())
    st.markdown(css, unsafe_allow_html=True)

def render_header(app_title: str = "Carioca", full_name: str = "", avatar_data: str | None = None):
    apply_minimal_theme()
    name_html = f'<div class="subtitle">{full_name}</div>' if full_name else ""
    avatar_html = f'<img src="{avatar_data}" class="user-img"/>' if avatar_data else ""
    st.markdown(f"""
    <div class="carioca-header">
        <div class="title">{app_title}</div>
        {name_html}
        {avatar_html}
    </div>
    """, unsafe_allow_html=True)
