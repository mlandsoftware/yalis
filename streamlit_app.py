import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import urllib.parse
import requests
from io import BytesIO

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="YALIS | Luxury Footwear", layout="wide")

WHATSAPP_NUMBER = "593978868363"

# --- CSS CONCORDANTE (ESTILO MARY LUNA) ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;800&display=swap');

/* Fondo y Fuente */
.stApp { 
    background-color: #FFFFFF; 
    font-family: 'Montserrat', sans-serif; 
}

/* LA TARJETA (Contenedor de Streamlit) */
[data-testid="stVerticalBlockBorderWrapper"] {
    border: 1.5px solid #E91E63 !important; /* Borde fucsia Mary Luna */
    border-radius: 25px !important;
    padding: 20px !important;
    background-color: white !important;
    transition: all 0.3s ease-in-out !important;
}

[data-testid="stVerticalBlockBorderWrapper"]:hover {
    box-shadow: 0 10px 20px rgba(233, 30, 99, 0.15) !important;
    transform: translateY(-5px);
}

/* 1. NOMBRE (Arriba y alineado) */
.product-title {
    color: #E91E63;
    font-weight: 800;
    font-size: 1.1rem;
    text-transform: uppercase;
    margin-bottom: 12px;
    display: block;
    line-height: 1.2;
}

/* 2. FOTO (Cuadrada y contenida) */
[data-testid="stImage"] img {
    border-radius: 15px !important;
    aspect-ratio: 1 / 1 !important;
    object-fit: cover !important;
    border: 1px solid #f0f0f0;
}

/* 3. SECCIÓN PRECIO Y BOTÓN */
.price-tag {
    font-weight: 600;
    font-size: 1.3rem;
    color: #333;
    margin-top: 10px;
}

/* BOTÓN COMPRAR (Estilo Ovalado Fucsia) */
.stButton > button {
    background: transparent !important;
    color: #E91E63 !important;
    border: 1.5px solid #E91E63 !important;
    border-radius: 50px !important; /* Estilo píldora */
    padding: 8px 25px !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    width: 100% !important;
    text-transform: uppercase;
    letter-spacing: 1px;
    transition: all 0.3s ease !important;
}

.stButton > button:hover {
    background: #E91E63 !important;
    color: white !important;
}

/* Limpieza de interfaz */
header, footer {visibility: hidden;}
[data-testid="stHeader"] {background: rgba(0,0,0,0);}
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

# --- DIÁLOGO DE COMPRA ---
@st.dialog("FINALIZAR COMPRA")
def comprar_producto(row):
    st.markdown(f"<h2 style='color:#E91E63; font-weight:800;'>{row['Nombre']}</h2>", unsafe_allow_html=True)
    col_img, col_det = st.columns([1, 1])
    with col_img:
        data = get_image_from_drive(row["Imagen 1 link de la primera imagen"])
        if data: st.image(data, use_container_width=True)
    with col_det:
        st.write(f"### Precio: ${row['Precio']}")
        tallas = str(row["Tallas"]).split(',')
        talla_sel = st.selectbox("Selecciona tu talla:", tallas)
        cantidad = st.number_input("Cantidad:", min_value=1, step=1)
        
        wa_url = f"https://wa.me/{WHATSAPP_NUMBER}?text=Deseo comprar: {row['Nombre']} - Talla: {talla_sel}"
        st.markdown(f'''
            <a href="{wa_url}" target="_blank" style="text-decoration:none;">
                <div style="background:#25D366; color:white; text-align:center; padding:15px; border-radius:50px; font-weight:bold; margin-top:20px;">
                    PEDIR POR WHATSAPP
                </div>
            </a>
        ''', unsafe_allow_html=True)

# --- CABECERA ---
st.markdown('<div style="text-align:center; padding-bottom:40px;"><h1 style="color:#E91E63; font-weight:800; font-size:3rem;">YALIS</h1><p style="color:#666; letter-spacing:5px;">LUXURY FOOTWEAR</p></div>', unsafe_allow_html=True)

# --- CATÁLOGO ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(ttl="5m").dropna(subset=['Nombre'])

    # Grid de 3 columnas
    cols = st.columns(3)
    for index, row in df.iterrows():
        with cols[index % 3]:
            # El "border=True" es vital para que el CSS de la tarjeta se aplique correctamente
            with st.container(border=True):
                # 1. NOMBRE
                st.markdown(f'<span class="product-title">{row["Nombre"]}</span>', unsafe_allow_html=True)
                
                # 2. FOTO
                portada = get_image_from_drive(row["Imagen 1 link de la primera imagen"])
                if portada:
                    st.image(portada, use_container_width=True)
                else:
                    st.error("Imagen no disponible")
                
                # 3. PRECIO Y BOTÓN
                st.markdown(f'<div class="price-tag">${row["Precio"]}</div>', unsafe_allow_html=True)
                
                # Botón con palabra "COMPRAR"
                if st.button("COMPRAR", key=f"btn_{row['cod.']}"):
                    comprar_producto(row)

except Exception as e:
    st.error("Conectando con el inventario de YALIS...")
