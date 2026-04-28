import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import urllib.parse
import requests
from io import BytesIO

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="YALIS | Luxury Footwear", layout="wide")

WHATSAPP_NUMBER = "593978868363"

# --- CSS REFORZADO ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;800&display=swap');

.stApp { background-color: #FFFFFF; font-family: 'Montserrat', sans-serif; }

/* Forzamos que el contenedor de Streamlit no rompa el diseño */
[data-testid="stVerticalBlock"] > div:has(div.product-card) {
    padding: 0px !important;
}

.product-card {
    background: #FFFFFF;
    border: 1.5px solid #E91E63; /* Borde fucsia visible */
    border-radius: 25px;
    padding: 20px;
    margin-bottom: 20px;
    display: block;
    box-shadow: 0 4px 15px rgba(233, 30, 99, 0.1);
}

/* 1. NOMBRE */
.product-title {
    color: #E91E63;
    font-weight: 800;
    font-size: 1.1rem;
    text-transform: uppercase;
    margin-bottom: 15px;
    display: block;
}

/* 2. FOTO (Proporción 1:1) */
.img-container img {
    width: 100%;
    aspect-ratio: 1 / 1;
    object-fit: cover;
    border-radius: 15px;
    margin-bottom: 15px;
}

/* 3. CONTENEDOR INFERIOR */
.bottom-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 10px;
}

.product-price {
    font-weight: 700;
    font-size: 1.3rem;
    color: #333;
}

/* BOTÓN ESTILO PILL */
.stButton > button {
    background: transparent !important;
    color: #E91E63 !important;
    border: 1.5px solid #E91E63 !important;
    border-radius: 50px !important;
    padding: 5px 20px !important;
    font-weight: 600 !important;
    transition: 0.3s !important;
}

.stButton > button:hover {
    background: #E91E63 !important;
    color: white !important;
}

header, footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

@st.cache_data(show_spinner=False)
def get_image_from_drive(url):
    if not isinstance(url, str) or "drive.google.com" not in url: return None
    try:
        file_id = url.split('/d/')[1].split('/')[0] if "file/d/" in url else url.split('id=')[1].split('&')[0]
        direct_url = f"https://drive.google.com/uc?export=download&id={file_id}"
        return BytesIO(requests.get(direct_url).content)
    except: return None

@st.dialog("DETALLES")
def comprar_producto(row):
    st.write(f"### {row['Nombre']}")
    img = get_image_from_drive(row["Imagen 1 link de la primera imagen"])
    if img: st.image(img, use_container_width=True)
    st.write(f"**Precio: ${row['Precio']}**")
    talla = st.selectbox("Talla", str(row["Tallas"]).split(','))
    if st.button("Pedir por WhatsApp"):
        mensaje = urllib.parse.quote(f"Hola, quiero los {row['Nombre']} en talla {talla}")
        st.markdown(f'<meta http-equiv="refresh" content="0; url=https://wa.me/{WHATSAPP_NUMBER}?text={mensaje}">', unsafe_allow_html=True)

# --- CATÁLOGO ---
st.title("YALIS LUXURY")

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(ttl="5m").dropna(subset=['Nombre'])
    
    cols = st.columns(3)
    for i, row in df.iterrows():
        with cols[i % 3]:
            # Todo el contenido se genera en bloques que Streamlit coloca secuencialmente
            # Usamos contenedores de cierre/apertura para "envolver" visualmente
            
            st.markdown(f'''
                <div class="product-card">
                    <div class="product-title">{row["Nombre"]}</div>
                    <div class="img-container">
            ''', unsafe_allow_html=True)
            
            # 2. FOTO (Componente nativo de Streamlit)
            portada = get_image_from_drive(row["Imagen 1 link de la primera imagen"])
            if portada:
                st.image(portada, use_container_width=True)
            
            st.markdown(f'''
                    </div>
                    <div class="bottom-row">
                        <div class="product-price">${row["Precio"]}</div>
            ''', unsafe_allow_html=True)
            
            # 3. BOTÓN (Componente nativo de Streamlit)
            if st.button("VER", key=f"btn_{row['cod.']}"):
                comprar_producto(row)
            
            st.markdown('</div></div>', unsafe_allow_html=True) # Cerramos bottom-row y product-card

except Exception as e:
    st.error("Conectando...")
