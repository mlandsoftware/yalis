import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import urllib.parse
import requests
from io import BytesIO

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="YALIS | Luxury Footwear", layout="wide")

WHATSAPP_NUMBER = "593978868363"

# --- DISEÑO CSS ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;800&display=swap');

.stApp { background-color: #FFFFFF; font-family: 'Montserrat', sans-serif; }

/* Contenedor principal de la tarjeta (el borde fucsia) */
[data-testid="stVerticalBlockBorderWrapper"] > div > [data-testid="stVerticalBlock"] > div > div[class*="st-key-card_"] {
    border: 1px solid #E91E63 !important;
    border-radius: 25px !important;
    padding: 20px !important;
    background-color: white !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.05) !important;
}

/* 1. NOMBRE */
.product-title {
    color: #E91E63;
    font-weight: 800;
    font-size: 1.1rem;
    text-transform: uppercase;
    margin-bottom: 10px;
}

/* 2. PRECIO */
.product-price {
    font-weight: 600;
    font-size: 1.3rem;
    color: #333;
}

/* BOTÓN OVALADO */
.stButton > button {
    background: transparent !important;
    color: #E91E63 !important;
    border: 1px solid #E91E63 !important;
    border-radius: 30px !important;
    padding: 5px 20px !important;
    font-size: 0.8rem !important;
    font-weight: 600 !important;
}

.stButton > button:hover {
    background: #E91E63 !important;
    color: white !important;
}

header, footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- LÓGICA DE IMÁGENES ---
@st.cache_data(show_spinner=False)
def get_image_from_drive(url):
    if not isinstance(url, str) or "drive.google.com" not in url: return None
    try:
        file_id = url.split('/d/')[1].split('/')[0] if "file/d/" in url else url.split('id=')[1].split('&')[0]
        direct_url = f"https://drive.google.com/uc?export=download&id={file_id}"
        response = requests.get(direct_url, timeout=10)
        return BytesIO(response.content) if response.status_code == 200 else None
    except: return None

@st.dialog("DETALLES")
def comprar_producto(row):
    st.markdown(f"## {row['Nombre']}")
    # ... (resto de la lógica del modal igual)

# --- CABECERA ---
st.markdown('<h1 style="text-align:center; color:#E91E63;">YALIS LUXURY</h1>', unsafe_allow_html=True)

# --- CATÁLOGO ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(ttl="5m").dropna(subset=['Nombre'])

    cols = st.columns(3)
    for index, row in df.iterrows():
        with cols[index % 3]:
            # Usamos st.container con una llave única para aplicar el CSS del borde
            with st.container(key=f"card_{row['cod.']}"):
                
                # 1. NOMBRE
                st.markdown(f'<div class="product-title">{row["Nombre"]}</div>', unsafe_allow_html=True)
                
                # 2. FOTO (Proporción corregida)
                portada = get_image_from_drive(row["Imagen 1 link de la primera imagen"])
                if portada:
                    st.image(portada, use_container_width=True)
                
                # 3. PRECIO Y BOTÓN
                c1, c2 = st.columns([1, 1.2])
                with c1:
                    st.markdown(f'<div class="product-price">${row["Precio"]}</div>', unsafe_allow_html=True)
                with c2:
                    if st.button("VER DETALLES", key=f"btn_{row['cod.']}"):
                        comprar_producto(row)

except Exception as e:
    st.error("Conectando...")
