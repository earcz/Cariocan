import streamlit as st

BG_URL = "https://images.unsplash.com/photo-1544986581-efac024faf62?q=80&w=1400&auto=format&fit=crop"

def apply_base_bg():
    st.markdown(f"""
    <style>
    .stApp {{
      background: url('{BG_URL}') no-repeat center center fixed;
      background-size: cover;
    }}
    .block-container {{
      backdrop-filter: blur(6px);
      background-color: rgba(255,255,255,0.88);
      border-radius: 24px;
      padding: 2rem 2.2rem;
    }}
    </style>
    """, unsafe_allow_html=True)

def css_tropical():
    return """
    <style>
    .stApp { background-image: none !important; background: linear-gradient(135deg,#FF7E5F 0%,#FFB88C 40%,#FFD86F 70%,#FF5F6D 100%) fixed; }
    .block-container { backdrop-filter: blur(6px); background-color: rgba(255,255,255,0.88); border-radius: 24px; padding: 2rem 2.2rem; }
    .metric-card { border-radius: 16px; padding: 16px; background: rgba(255,255,255,0.75); border: 1px solid rgba(255,255,255,0.6); }
    .pill { padding: 4px 10px; border-radius: 999px; background: rgba(0,0,0,0.06); font-size: 12px; font-weight: 600; }
    img.muscle { max-width: 140px; border-radius: 12px; border: 1px solid #fff; box-shadow: 0 4px 18px rgba(0,0,0,0.15); }
    header .e1fb0d4c1 { display: none !important; }
    </style>
    """

def css_minimal():
    return """
    <style>
    .stApp { background-image: none !important; background: #f5f7fb; }
    .block-container { background: #ffffff; border: 1px solid #e5e7eb; border-radius: 16px; padding: 2rem 2.2rem; }
    .metric-card { border-radius: 12px; padding: 14px; background: #fff; border: 1px solid #e5e7eb; }
    .pill { padding: 3px 8px; border-radius: 12px; background: #eef2ff; font-size: 12px; font-weight: 600; }
    img.muscle { max-width: 140px; border-radius: 12px; border: 1px solid #e5e7eb; }
    header .e1fb0d4c1 { display: none !important; }
    </style>
    """

def header(title: str, subtitle: str = "", avatar_b64: str | None = None, theme: str = "tropical"):
    st.markdown(css_tropical() if theme == "tropical" else css_minimal(), unsafe_allow_html=True)
    c1, c2 = st.columns([7,1])
    with c1:
        st.title(title)
        if subtitle:
            st.caption(subtitle)
    with c2:
        if avatar_b64:
            st.image(avatar_b64, width=88)
