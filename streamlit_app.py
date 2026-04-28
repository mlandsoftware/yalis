import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import urllib.parse
import requests
from io import BytesIO

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="YALIS | Luxury Footwear", layout="wide")

WHATSAPP_NUMBER = "593978868363"

# --- CSS REFINADO: TARJETAS Y MODAL ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;800&display=swap');

/* Aplicar Montserrat a toda la app, incluyendo diálogos */
.stApp, [data-testid="stDialog"] { 
    background-color: #FFFFFF; 
    font-family: 'Montserrat', sans-serif !important; 
}

/* ========== ESTILO DEL MODAL (VENTANA EMERGENTE) ========== */
div[data-testid="stDialog"] {
    background-color: white !important;
    border-radius: 20px !important;
}

div[data-testid="stDialog"] h2 {
    font-family: 'Montserrat', sans-serif !important;
    font-weight: 800 !important;
    text-transform: uppercase;
}

/* ========== TARJETA DEL CATÁLOGO ========== */
div[data-testid="stVerticalBlockBorderWrapper"] > div {
    border: 2px solid #E91E63 !important;
    border-radius: 25px !important;
    padding: 20px !important;
    background-color: white !important;
    transition: all 0.3s ease-in-out !important;
}

div[data-testid="stVerticalBlockBorderWrapper"] > div:hover {
    transform: translateY(-5px) !important;
    box-shadow: 0 12px 30px rgba(233, 30, 99, 0.2) !important;
}

.product-title {
    color: #E91E63;
    font-weight: 800;
    font-size: 1.4rem;
    text-transform: uppercase;
    text-align: center;
    display: block;
    margin-bottom: -15px !important;
    line-height: 1.1;
}

[data-testid="stImage"] img {
    border-radius: 15px !important;
    aspect-ratio: 1 / 1 !important;
    object-fit: cover !important;
}

.price-container {
    font-weight: 600;
    font-size: 1.3rem;
    color: #333;
}

/* BOTÓN COMPRAR EN TARJETA */
.stButton > button {
    background: transparent !important;
    color: #E91E63 !important;
    border: 2px solid #E91E63 !important;
    border-radius: 50px !important;
    font-weight: 700 !important;
    text-transform: uppercase;
    width: 100% !important;
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

# --- VENTANA EMERGENTE (MODAL) ---
@st.dialog("DETALLES DEL PRODUCTO")
def comprar_producto(row):
    # Fondo blanco y tipografía forzada
    st.markdown(f"""
        <h2 style='color:#E91E63; text-align:center; font-family:Montserrat;'>{row['Nombre']}</h2>
        <hr style="border: 0.5px solid #f0f0f0;">
    """, unsafe_allow_html=True)
    
    col_img, col_det = st.columns([1.2, 1])
    
    with col_img:
        data = get_image_from_drive(row["Imagen 1 link de la primera imagen"])
        if data: 
            st.image(data, use_container_width=True)
    
    with col_det:
        st.markdown(f"<h3 style='font-family:Montserrat;'>Precio: ${row['Precio']}</h3>", unsafe_allow_html=True)
        st.markdown(f"<p style='font-family:Montserrat; color:#666;'>Colección: {row['Coleccion']}</p>", unsafe_allow_html=True)
        
        tallas = str(row["Tallas"]).split(',')
        talla_sel = st.selectbox("Selecciona tu talla:", tallas)
        
        # Botón de WhatsApp con texto negro y fondo sutil
        mensaje = f"Hola YALIS, deseo comprar: {row['Nombre']} en Talla: {talla_sel}"
        wa_url = f"https://wa.me/{WHATSAPP_NUMBER}?text={urllib.parse.quote(mensaje)}"
        
        st.markdown(f"""
            <a href="{wa_url}" target="_blank" style="text-decoration:none;">
                <div style="
                    background-color: #f8f9fa; 
                    color: black; 
                    text-align: center; 
                    padding: 15px; 
                    border-radius: 50px; 
                    font-weight: 800; 
                    border: 2px solid #25D366;
                    margin-top: 20px;
                    font-family: 'Montserrat', sans-serif;
                    text-transform: uppercase;
                    letter-spacing: 1px;">
                    Pedir por WhatsApp
                </div>
            </a>
        """, unsafe_allow_html=True)

# --- CABECERA ---
st.markdown('<h1 style="text-align:center; color:#E91E63; font-weight:800; margin-bottom:40px; font-family:Montserrat;">YALIS LUJO</h1>', unsafe_allow_html=True)

# --- CATÁLOGO ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(ttl="5m").dropna(subset=['Nombre'])

    main_cols = st.columns(3)
    for index, row in df.iterrows():
        with main_cols[index % 3]:
            with st.container(border=True):
                st.markdown(f'<span class="product-title">{row["Nombre"]}</span>', unsafe_allow_html=True)
                
                portada = get_image_from_drive(row["Imagen 1 link de la primera imagen"])
                if portada:
                    st.image(portada, use_container_width=True)
                
                c_pre, c_btn = st.columns([1, 1.2])
                with c_pre:
                    st.markdown(f'<div class="price-container">${row["Precio"]}</div>', unsafe_allow_html=True)
                with c_btn:
                    if st.button("COMPRAR", key=f"btn_{row['cod.']}"):
                        comprar_producto(row)

except Exception as e:
    st.error("Conectando con el inventario...")
