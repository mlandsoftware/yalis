import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import urllib.parse
import requests
from io import BytesIO
import base64

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="YALIS | Luxury Footwear", layout="wide")

WHATSAPP_NUMBER = "593978868363"

# --- DISEÑO CSS ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;800&display=swap');

.stApp { background-color: #FFFFFF; font-family: 'Montserrat', sans-serif; }

/* LA TARJETA CONTENEDORA */
.product-card {
    background: #FFFFFF;
    border: 1px solid #E91E63;
    border-radius: 20px;
    padding: 20px;
    margin-bottom: 25px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    display: flex;
    flex-direction: column;
}

/* 1. NOMBRE */
.product-title {
    color: #E91E63;
    font-weight: 800;
    font-size: 1.1rem;
    text-transform: uppercase;
    margin-bottom: 15px;
    min-height: 45px;
}

/* 2. FOTO */
.img-container {
    width: 100%;
    aspect-ratio: 1 / 1;
    border-radius: 15px;
    overflow: hidden;
    margin-bottom: 15px;
}
.img-container img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

/* 3. PRECIO Y BOTÓN */
.bottom-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 10px;
}
.product-price {
    font-weight: 600;
    font-size: 1.3rem;
    color: #333;
}

/* Estilo para el link que parece botón */
.view-btn {
    background: transparent;
    color: #E91E63;
    border: 1px solid #E91E63;
    border-radius: 30px;
    padding: 6px 15px;
    text-decoration: none;
    font-size: 0.8rem;
    font-weight: 600;
    transition: 0.3s;
}
.view-btn:hover {
    background: #E91E63;
    color: white;
}

header, footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- FUNCIÓN PARA IMÁGENES (Convertir a Base64 para HTML) ---
def get_image_base64(url):
    if not isinstance(url, str) or "drive.google.com" not in url:
        return ""
    try:
        file_id = url.split('/d/')[1].split('/')[0] if "file/d/" in url else url.split('id=')[1].split('&')[0]
        direct_url = f"https://drive.google.com/uc?export=download&id={file_id}"
        response = requests.get(direct_url, timeout=10)
        if response.status_code == 200:
            return base64.b64encode(response.content).decode()
    except:
        return ""
    return ""

# --- DIÁLOGO DE DETALLES ---
@st.dialog("DETALLES DEL CALZADO")
def ver_detalles(row):
    st.write(f"### {row['Nombre']}")
    # Aquí puedes añadir el contenido del modal como lo tenías antes
    st.write(f"Precio: ${row['Precio']}")
    st.write(f"Tallas: {row['Tallas']}")
    # ... resto de tu lógica de WhatsApp ...

# --- CATÁLOGO ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(ttl="5m").dropna(subset=['Nombre'])

    cols = st.columns(3)
    for index, row in df.iterrows():
        with cols[index % 3]:
            # Obtenemos la imagen en base64 para que el HTML no dependa de componentes externos
            img_b64 = get_image_base64(row["Imagen 1 link de la primera imagen"])
            img_html = f"data:image/png;base64,{img_b64}" if img_b64 else "https://via.placeholder.com/400"
            
            # ESTRUCTURA ÚNICA DENTRO DE LA TARJETA
            st.markdown(f"""
                <div class="product-card">
                    <div class="product-title">{row['Nombre']}</div>
                    <div class="img-container">
                        <img src="{img_html}">
                    </div>
                    <div class="bottom-row">
                        <div class="product-price">${row['Precio']}</div>
                        <a href="?prod={row['cod.']}" class="view-btn">VER DETALLES</a>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Nota: Como Streamlit no permite botones nativos dentro de HTML inyectado fácilmente,
            # lo ideal es usar el query_params o botones invisibles de Streamlit debajo, 
            # pero para que el diseño no se rompa, esta estructura HTML es la que garantiza el diseño de la imagen.

            if st.button("Abrir Detalles", key=f"btn_{row['cod.']}", use_container_width=True):
                ver_detalles(row)

except Exception as e:
    st.error("Conectando con inventario...")
