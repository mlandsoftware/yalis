import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import urllib.parse
import requests
from io import BytesIO

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="YALIS SHOES | Calzado para dama", layout="wide")

WHATSAPP_NUMBER = "593978868363"

# --- CSS INTEGRADO OPTIMIZADO ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;800&display=swap');

/* Configuración base */
.stApp { 
    background-color: #FFFFFF; 
    font-family: 'Montserrat', sans-serif !important; 
}

/* CONTENEDOR DE TARJETA (ALTURA FIJA PARA ALINEACIÓN) */
[data-testid="stVerticalBlockBorderWrapper"] > div {
    border: 2px solid #E91E63 !important;
    border-radius: 20px !important;
    padding: 15px !important;
    background-color: white !important;
    transition: all 0.3s ease-in-out !important;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    height: 450px; /* Altura fija de la tarjeta para que todas sean iguales */
}

/* CONTENEDOR DE IMAGEN UNIFORME */
.img-container {
    width: 100%;
    height: 250px; /* Altura fija para la zona de la imagen */
    display: flex;
    justify-content: center;
    align-items: center;
    overflow: hidden;
    margin: 10px 0;
}

.img-container img {
    max-width: 100%;
    max-height: 100%;
    object-fit: contain; /* Ajusta la imagen sin deformarla ni recortarla */
}

/* TÍTULOS */
.product-title {
    color: #E91E63;
    font-weight: 800;
    font-size: 1.1rem;
    text-transform: uppercase;
    text-align: center;
    display: block;
    min-height: 45px; /* Espacio para 2 líneas de texto */
}

.product-price-cat {
    font-weight: 800;
    font-size: 1.4rem;
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
    transition: 0.3s;
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
def get_image_url(url):
    """Convierte el link de Drive en un link directo de imagen"""
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
    
    with col_img:
        img_link = get_image_url(row["Imagen 1 link de la primera imagen"])
        if img_link:
            st.image(img_link, use_container_width=True)
            
    with col_det:
        st.markdown(f"<h3 style='color:#000;'>${row['Precio']}</h3>", unsafe_allow_html=True)
        st.markdown(f"<p style='color:#000;'><b>Colección:</b> {row['Coleccion']}</p>", unsafe_allow_html=True)
        
        tallas = str(row["Tallas"]).split(',')
        talla_sel = st.selectbox("Selecciona tu talla:", tallas)
        
        mensaje = f"Hola YALIS, deseo comprar: {row['Nombre']} en talla {talla_sel}"
        wa_url = f"https://wa.me/{WHATSAPP_NUMBER}?text={urllib.parse.quote(mensaje)}"
        
        st.markdown(f'<a href="{wa_url}" target="_blank" style="text-decoration:none;"><div style="background-color:#25D366; color:#fff; text-align:center; padding:12px; border-radius:50px; font-weight:800; margin-top:10px;">WHATSAPP</div></a>', unsafe_allow_html=True)

# --- CABECERA ---
st.markdown('<h1 style="text-align:center; color:#E91E63; font-weight:800; margin-bottom:40px;">YALIS SHOES</h1>', unsafe_allow_html=True)

# --- CATÁLOGO ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(ttl="5m").dropna(subset=['Nombre'])

    cols = st.columns(3)
    for index, row in df.iterrows():
        with cols[index % 3]:
            with st.container(border=True):
                # 1. NOMBRE
                st.markdown(f'<span class="product-title">{row["Nombre"]}</span>', unsafe_allow_html=True)
                
                # 2. FOTO (USANDO HTML PARA CONTROLAR EL TAMAÑO)
                img_url = get_image_url(row["Imagen 1 link de la primera imagen"])
                st.markdown(f'''
                    <div class="img-container">
                        <img src="{img_url}">
                    </div>
                ''', unsafe_allow_html=True)
                
                # 3. PRECIO
                st.markdown(f'<div class="product-price-cat">${row["Precio"]}</div>', unsafe_allow_html=True)
                
                # 4. BOTÓN
                if st.button("COMPRAR", key=f"btn_{row.get('cod.', index)}"):
                    comprar_producto(row)

except Exception as e:
    st.error("Estamos actualizando el catálogo, por favor espera...")
