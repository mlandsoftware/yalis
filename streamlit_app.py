import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import urllib.parse
import requests
from io import BytesIO

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="YALIS SHOES | Calzado para dama", layout="wide")

WHATSAPP_NUMBER = "593978868363"

# --- CSS INTEGRADO CORREGIDO ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;800&display=swap');

/* Configuración base */
.stApp { 
    background-color: #FFFFFF; 
    font-family: 'Montserrat', sans-serif !important; 
}

/* FUERZA LA MISMA ALTURA EN LAS TARJETAS */
[data-testid="stVerticalBlock"] > div:has(div.product-card) {
    display: flex;
    flex-direction: column;
    height: 100%;
}

/* TARJETA DEL CATÁLOGO (SELECTOR MÁS FUERTE) */
div.product-card {
    border: 2px solid #E91E63 !important;
    border-radius: 25px !important;
    padding: 20px !important;
    background-color: white !important;
    transition: all 0.3s ease-in-out !important;
    height: 100% !important;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    margin-bottom: 20px;
}

div.product-card:hover {
    transform: translateY(-8px) !important;
    box-shadow: 0 12px 30px rgba(233, 30, 99, 0.3) !important;
    border-color: #C2185B !important;
}

/* TÍTULOS */
.product-title {
    color: #E91E63;
    font-weight: 800;
    font-size: 1.2rem;
    text-transform: uppercase;
    text-align: center;
    display: block;
    min-height: 50px; /* Asegura espacio para nombres largos */
}

.product-price-cat {
    font-weight: 700;
    font-size: 1.4rem;
    color: #333;
    text-align: left;
}

/* BOTÓN COMPRAR */
.stButton > button {
    background: transparent !important;
    color: #E91E63 !important;
    border: 2px solid #E91E63 !important;
    border-radius: 50px !important;
    font-weight: 700 !important;
    text-transform: uppercase;
    width: 100% !important;
    transition: 0.3s;
}

.stButton > button:hover {
    background: #E91E63 !important;
    color: white !important;
}

/* MODAL / DIALOG */
div[data-testid="stDialog"] div[role="dialog"] {
    background-color: #FFFFFF !important;
    border-radius: 20px !important;
}

div[data-testid="stDialog"] h2, 
div[data-testid="stDialog"] h3, 
div[data-testid="stDialog"] p, 
div[data-testid="stDialog"] label {
    color: #000000 !important;
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
    st.markdown(f"<h2 style='color:#E91E63; font-family:Montserrat; font-weight:800; text-align:center;'>{row['Nombre']}</h2>", unsafe_allow_html=True)
    
    col_img, col_det = st.columns([1.2, 1])
    
    with col_img:
        data = get_image_from_drive(row["Imagen 1 link de la primera imagen"])
        if data:
            st.image(data, use_container_width=True)
            
    with col_det:
        st.markdown(f"<h3 style='color:#000000; font-family:Montserrat;'>${row['Precio']}</h3>", unsafe_allow_html=True)
        st.markdown(f"<p style='color:#000000;'><b>Colección:</b> {row['Coleccion']}</p>", unsafe_allow_html=True)
        
        tallas = str(row["Tallas"]).split(',')
        talla_sel = st.selectbox("Selecciona tu talla:", tallas)
        
        mensaje = f"Hola YALIS, deseo comprar: {row['Nombre']} en talla {talla_sel}"
        wa_url = f"https://wa.me/{WHATSAPP_NUMBER}?text={urllib.parse.quote(mensaje)}"
        
        st.markdown(f'''
            <a href="{wa_url}" target="_blank" style="text-decoration:none;">
                <div style="
                    background-color: #25D366; 
                    color: white; 
                    text-align: center; 
                    padding: 12px; 
                    border-radius: 50px; 
                    font-weight: 800; 
                    font-family: Montserrat;
                    margin-top: 10px;
                    border: none;">
                    PEDIR POR WHATSAPP
                </div>
            </a>
        ''', unsafe_allow_html=True)

# --- CABECERA ---
st.markdown('<h1 style="text-align:center; color:#E91E63; font-weight:800; margin-bottom:40px;">YALIS SHOES</h1>', unsafe_allow_html=True)

# --- CATÁLOGO ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(ttl="5m").dropna(subset=['Nombre'])

    # Creamos las filas del catálogo
    for i in range(0, len(df), 3):
        cols = st.columns(3)
        for j in range(3):
            if i + j < len(df):
                row = df.iloc[i + j]
                with cols[j]:
                    # Usamos un div con clase personalizada para aplicar el estilo
                    st.markdown('<div class="product-card">', unsafe_allow_html=True)
                    
                    # 1. NOMBRE
                    st.markdown(f'<span class="product-title">{row["Nombre"]}</span>', unsafe_allow_html=True)
                    
                    # 2. FOTO
                    portada = get_image_from_drive(row["Imagen 1 link de la primera imagen"])
                    if portada:
                        st.image(portada, use_container_width=True)
                    else:
                        st.write("Cargando imagen...")
                    
                    # 3. PRECIO Y BOTÓN
                    c_pre, c_btn = st.columns([1, 1.2])
                    with c_pre:
                        st.markdown(f'<div class="product-price-cat">${row["Precio"]}</div>', unsafe_allow_html=True)
                    with c_btn:
                        if st.button("COMPRAR", key=f"btn_{row.get('cod.', i+j)}"):
                            comprar_producto(row)
                    
                    st.markdown('</div>', unsafe_allow_html=True)

except Exception as e:
    st.error(f"Error al cargar el inventario: {e}")
