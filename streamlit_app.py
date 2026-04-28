import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import urllib.parse
import requests
from io import BytesIO

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="YALIS SHOES | Calzado para dama", layout="wide")

WHATSAPP_NUMBER = "593978868363"

# --- CSS INTEGRADO (Incluye regularización de imágenes y footer) ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;800&display=swap');

.stApp { 
    background-color: #FFFFFF; 
    font-family: 'Montserrat', sans-serif !important; 
}

/* REGULARIZACIÓN DE TARJETAS */
div[data-testid="stVerticalBlockBorderWrapper"] > div {
    border: 2px solid #E91E63 !important;
    border-radius: 20px !important;
    padding: 15px !important;
    background-color: white !important;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    height: 480px; /* Altura fija para alineación total */
}

/* CONTENEDOR DE IMAGEN UNIFORME */
.img-container {
    width: 100%;
    height: 250px;
    display: flex;
    justify-content: center;
    align-items: center;
    overflow: hidden;
    margin: 5px 0;
}
.img-container img {
    max-width: 100%;
    max-height: 100%;
    object-fit: contain;
}

.product-title {
    color: #E91E63;
    font-weight: 800;
    font-size: 1.2rem;
    text-transform: uppercase;
    text-align: center;
    min-height: 50px;
}

.product-price-cat {
    font-weight: 700;
    font-size: 1.3rem;
    color: #333;
    text-align: center;
}

/* BOTÓN COMPRAR */
.stButton > button {
    background: transparent !important;
    color: #E91E63 !important;
    border: 2px solid #E91E63 !important;
    border-radius: 50px !important;
    font-weight: 700 !important;
    width: 100% !important;
}
.stButton > button:hover {
    background: #E91E63 !important;
    color: white !important;
}

/* FOOTER ESTILIZADO */
.footer {
    position: relative;
    left: 0;
    bottom: 0;
    width: 100%;
    background-color: #f8f9fa;
    color: #666;
    text-align: center;
    padding: 20px 0;
    margin-top: 50px;
    border-top: 1px solid #eee;
}

header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- LÓGICA DE IMÁGENES (Conversión a link directo) ---
def get_direct_img_link(url):
    if not isinstance(url, str) or "drive.google.com" not in url: return ""
    try:
        file_id = url.split('/d/')[1].split('/')[0] if "file/d/" in url else url.split('id=')[1].split('&')[0]
        return f"https://drive.google.com/uc?export=view&id={file_id}"
    except: return ""

# --- VENTANA EMERGENTE (MODAL) ---
@st.dialog("Detalle del producto")
def comprar_producto(row):
    st.markdown(f"<h2 style='color:#E91E63; font-weight:800; text-align:center;'>{row['Nombre']}</h2>", unsafe_allow_html=True)
    
    col_img, col_det = st.columns([1.2, 1])
    img_url = get_direct_img_link(row["Imagen 1 link de la primera imagen"])
    
    with col_img:
        if img_url: st.image(img_url, use_container_width=True)
            
    with col_det:
        st.markdown(f"<h3 style='color:#000;'>${row['Precio']}</h3>", unsafe_allow_html=True)
        st.markdown(f"<p style='color:#333;'><b>Colección:</b> {row['Coleccion']}</p>", unsafe_allow_html=True)
        
        tallas = str(row["Tallas"]).split(',')
        talla_sel = st.selectbox("Selecciona tu talla:", tallas)
        
        # --- MEJORA DEL MENSAJE DE WHATSAPP ---
        mensaje_wa = (
            f"🛍️ *NUEVO PEDIDO - YALIS SHOES*\n"
            f"------------------------------------------\n"
            f"👟 *Producto:* {row['Nombre']}\n"
            f"📏 *Talla:* {talla_sel}\n"
            f"💰 *Precio:* ${row['Precio']}\n"
            f"✨ *Colección:* {row['Coleccion']}\n"
            f"------------------------------------------\n"
            f"Por favor, confirmar disponibilidad para finalizar mi compra. 😊"
        )
        
        wa_url = f"https://wa.me/{WHATSAPP_NUMBER}?text={urllib.parse.quote(mensaje_wa)}"
        
        st.markdown(f'''
            <a href="{wa_url}" target="_blank" style="text-decoration:none;">
                <div style="background-color:#25D366; color:white; text-align:center; padding:12px; border-radius:50px; font-weight:800; margin-top:15px; border:1px solid #128C7E;">
                    PEDIR POR WHATSAPP
                </div>
            </a>
        ''', unsafe_allow_html=True)

# --- CUERPO DE LA PÁGINA ---
st.markdown('<h1 style="text-align:center; color:#E91E63; font-weight:800; margin-bottom:40px;">YALIS SHOES</h1>', unsafe_allow_html=True)

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(ttl="5m").dropna(subset=['Nombre'])

    main_cols = st.columns(3)
    for index, row in df.iterrows():
        with main_cols[index % 3]:
            with st.container(border=True):
                st.markdown(f'<span class="product-title">{row["Nombre"]}</span>', unsafe_allow_html=True)
                
                img_url = get_direct_img_link(row["Imagen 1 link de la primera imagen"])
                st.markdown(f'<div class="img-container"><img src="{img_url}"></div>', unsafe_allow_html=True)
                
                st.markdown(f'<div class="product-price-cat">${row["Precio"]}</div>', unsafe_allow_html=True)
                
                if st.button("VER DETALLES", key=f"btn_{index}"):
                    comprar_producto(row)

except Exception as e:
    st.error("Cargando catálogo...")

# --- FOOTER ---
st.markdown("""
    <div class="footer">
        <p><b>YALIS SHOES</b> - Calzado de Dama con Estilo<br>
        📍 Ecuador | 🚚 Envíos a todo el país<br>
        © 2026 Todos los derechos reservados</p>
    </div>
""", unsafe_allow_html=True)
