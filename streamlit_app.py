import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import urllib.parse
import requests
from io import BytesIO

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="YALIS | Luxury Footwear", layout="wide")

WHATSAPP_NUMBER = "593978868363"

# --- CSS INTEGRADO ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;800&display=swap');

.stApp, [data-testid="stDialog"] { 
    background-color: #FFFFFF; 
    font-family: 'Montserrat', sans-serif !important; 
}

/* MODAL */
div[data-testid="stDialog"] div[role="dialog"] {
    background-color: #FFFFFF !important;
    border-radius: 25px !important;
}

/* TARJETAS PRINCIPALES */
div[data-testid="stVerticalBlockBorderWrapper"] > div {
    border: 2px solid #E91E63 !important;
    border-radius: 25px !important;
    padding: 20px !important;
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
}

/* BOTÓN COMPRAR CATÁLOGO */
.stButton > button {
    background: transparent !important;
    color: #E91E63 !important;
    border: 2px solid #E91E63 !important;
    border-radius: 50px !important;
    font-weight: 700 !important;
    width: 100% !important;
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
@st.dialog("Detalle del producto")
def comprar_producto(row):
    # Título Fucsia
    st.markdown(f"<h2 style='color:#E91E63; font-weight:800; text-align:center; margin-bottom:15px;'>{row['Nombre']}</h2>", unsafe_allow_html=True)
    
    col_img, col_det = st.columns([1, 1])
    
    with col_img:
        data = get_image_from_drive(row["Imagen 1 link de la primera imagen"])
        if data:
            st.image(data, use_container_width=True)
            
    with col_det:
        # Agrupamos Precio y Colección en un solo bloque HTML para control total
        st.markdown(f"""
            <div style="text-align: left; margin-bottom: 10px;">
                <h1 style="color: #000000; font-weight: 800; margin: 0; font-size: 2.5rem;">${row['Precio']}</h1>
                <p style="color: #000000; margin: 5px 0; font-size: 1rem;"><b>Colección:</b> {row['Coleccion']}</p>
                <p style="color: #000000; margin: 20px 0 5px 0; font-size: 0.9rem;">Selecciona tu talla:</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Selector de Talla
        tallas = str(row["Tallas"]).split(',')
        talla_sel = st.selectbox("label_invisible", tallas, label_visibility="collapsed", key=f"mod_{row['cod.']}")
        
        # Botón WhatsApp
        mensaje = f"Hola YALIS, deseo comprar: {row['Nombre']} en talla {talla_sel}"
        wa_url = f"https://wa.me/{WHATSAPP_NUMBER}?text={urllib.parse.quote(mensaje)}"
        
        st.markdown(f'''
            <a href="{wa_url}" target="_blank" style="text-decoration:none;">
                <div style="
                    background-color: #25D366; 
                    color: #000000; 
                    text-align: center; 
                    padding: 15px; 
                    border-radius: 50px; 
                    font-weight: 800; 
                    margin-top: 20px;
                    border: 1px solid #128C7E;">
                    PEDIR POR WHATSAPP
                </div>
            </a>
        ''', unsafe_allow_html=True)

# --- APP PRINCIPAL ---
st.markdown('<h1 style="text-align:center; color:#E91E63; font-weight:800; margin-bottom:40px;">YALIS LUJO</h1>', unsafe_allow_html=True)

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(ttl="5m").dropna(subset=['Nombre'])
    cols = st.columns(3)
    for index, row in df.iterrows():
        with cols[index % 3]:
            with st.container(border=True):
                st.markdown(f'<span class="product-title">{row["Nombre"]}</span>', unsafe_allow_html=True)
                portada = get_image_from_drive(row["Imagen 1 link de la primera imagen"])
                if portada: st.image(portada, use_container_width=True)
                
                c1, c2 = st.columns([1, 1.2])
                c1.markdown(f"### ${row['Precio']}")
                if c2.button("COMPRAR", key=f"btn_{row['cod.']}"):
                    comprar_producto(row)
except:
    st.error("Error de conexión.")
