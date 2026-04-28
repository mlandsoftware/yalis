import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import urllib.parse
import requests
from io import BytesIO

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="YALIS | Luxury Footwear", layout="wide")

WHATSAPP_NUMBER = "593978868363"

# --- CSS REFINADO: AJUSTE DE TAMAÑO Y ESPACIOS ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;800&display=swap');

.stApp { background-color: #FFFFFF; font-family: 'Montserrat', sans-serif; }

/* TARJETA CON BORDE FUCSIA */
[data-testid="stVerticalBlockBorderWrapper"] {
    border: 2px solid #E91E63 !important;
    border-radius: 25px !important;
    padding: 15px 15px 25px 15px !important;
    background-color: white !important;
    box-shadow: 0 4px 15px rgba(233, 30, 99, 0.05) !important;
}

/* 1. NOMBRE: Más grande y más cerca de la imagen */
.product-title {
    color: #E91E63;
    font-weight: 800;
    font-size: 1.4rem; /* Aumentado 2 unidades aprox */
    text-transform: uppercase;
    text-align: center;
    display: block;
    margin-bottom: -15px; /* Margen negativo para acercar a la imagen */
    line-height: 1.1;
}

/* 2. IMAGEN: Proporción Cuadrada */
[data-testid="stImage"] img {
    border-radius: 15px !important;
    aspect-ratio: 1 / 1 !important;
    object-fit: cover !important;
}

/* Espaciado entre elementos internos de Streamlit */
[data-testid="stVerticalBlock"] > div {
    gap: 0.5rem !important;
}

/* 3. FILA DE PRECIO Y BOTÓN */
.price-container {
    font-weight: 600;
    font-size: 1.3rem;
    color: #333;
    text-align: left;
}

/* BOTÓN COMPRAR */
.stButton > button {
    background: transparent !important;
    color: #E91E63 !important;
    border: 2px solid #E91E63 !important;
    border-radius: 50px !important;
    padding: 5px 20px !important;
    font-weight: 700 !important;
    font-size: 0.85rem !important;
    width: 100% !important;
    transition: all 0.3s ease !important;
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
    st.markdown(f"<h2 style='color:#E91E63; text-align:center;'>{row['Nombre']}</h2>", unsafe_allow_html=True)
    col_img, col_det = st.columns([1.2, 1])
    with col_img:
        data = get_image_from_drive(row["Imagen 1 link de la primera imagen"])
        if data: st.image(data, use_container_width=True)
    with col_det:
        st.markdown(f"## ${row['Precio']}")
        tallas = str(row["Tallas"]).split(',')
        st.selectbox("Talla:", tallas)
        wa_url = f"https://wa.me/{WHATSAPP_NUMBER}?text=Comprar: {row['Nombre']}"
        st.markdown(f'<a href="{wa_url}" target="_blank" style="text-decoration:none;"><div style="background:#25D366; color:white; text-align:center; padding:12px; border-radius:50px; font-weight:bold; margin-top:20px;">WHATSAPP</div></a>', unsafe_allow_html=True)

# --- CABECERA ---
st.markdown('<h1 style="text-align:center; color:#E91E63; font-weight:800; margin-bottom:40px;">YALIS LUJO</h1>', unsafe_allow_html=True)

# --- CATÁLOGO ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(ttl="5m").dropna(subset=['Nombre'])

    main_cols = st.columns(3)
    for index, row in df.iterrows():
        with main_cols[index % 3]:
            with st.container(border=True):
                # 1. NOMBRE (CENTRADO Y MÁS GRANDE)
                st.markdown(f'<span class="product-title">{row["Nombre"]}</span>', unsafe_allow_html=True)
                
                # 2. FOTO (MÁS PEGADA AL NOMBRE)
                portada = get_image_from_drive(row["Imagen 1 link de la primera imagen"])
                if portada:
                    st.image(portada, use_container_width=True)
                
                # 3. PRECIO Y BOTÓN
                c_pre, c_btn = st.columns([1, 1.2])
                with c_pre:
                    st.markdown(f'<div class="price-container">${row["Precio"]}</div>', unsafe_allow_html=True)
                with c_btn:
                    if st.button("COMPRAR", key=f"btn_{row['cod.']}"):
                        comprar_producto(row)

except Exception as e:
    st.error("Error al cargar datos.")
