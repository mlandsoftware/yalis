import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import urllib.parse
import requests
from io import BytesIO

st.set_page_config(page_title="YALIS | Luxury Footwear", layout="wide")

WHATSAPP_NUMBER = "593978868363"

# CSS Maestro para Encapsulamiento Total
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&family=Montserrat:wght@300;400;600&display=swap');

    .stApp { background-color: #FFFFFF; }
    
    /* Contenedor de la Tarjeta */
    .product-card {
        background-color: #fcfcfc;
        border-radius: 15px;
        border: 1px solid #eeeeee;
        padding: 0px; /* Quitamos padding para que la imagen llegue al borde superior */
        margin-bottom: 30px;
        overflow: hidden; /* Esto mantiene todo adentro */
        transition: all 0.3s ease;
        display: flex;
        flex-direction: column;
        height: 100%;
        box-shadow: 0 10px 20px rgba(0,0,0,0.02);
    }
    
    .product-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 30px rgba(0,0,0,0.08);
        border-color: #D4AF37;
    }

    /* Ajuste de Imagen para que sea proporcional */
    .img-container {
        width: 100%;
        height: 350px; /* Altura fija para uniformidad en PC */
        overflow: hidden;
    }
    .img-container img {
        width: 100%;
        height: 100%;
        object-fit: cover; /* Recorta la imagen para llenar el espacio sin deformarse */
    }

    /* Área de texto dentro de la tarjeta */
    .info-container {
        padding: 20px;
        text-align: center;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        flex-grow: 1;
    }

    .product-title {
        font-family: 'Montserrat', sans-serif;
        font-size: 1.1rem;
        font-weight: 600;
        color: #1a1a1a;
        margin-bottom: 5px;
        height: 50px; /* Altura fija para que los precios se alineen */
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .product-price {
        color: #D4AF37;
        font-size: 1.2rem;
        font-weight: 400;
        margin-bottom: 15px;
    }

    /* Botón Minimalista */
    .stButton>button {
        background-color: #1a1a1a !important;
        color: #D4AF37 !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 10px !important;
        font-family: 'Cinzel', serif !important;
        font-size: 0.8rem !important;
        letter-spacing: 2px !important;
        transition: 0.3s !important;
    }
    
    .stButton>button:hover {
        background-color: #D4AF37 !important;
        color: #1a1a1a !important;
    }

    /* Responsive */
    @media (max-width: 768px) {
        .img-container { height: 450px; } /* Más alto en móvil para ver detalle */
    }

    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(show_spinner=False)
def get_image_from_drive(url):
    if not isinstance(url, str) or "drive.google.com" not in url: return None
    try:
        file_id = url.split('/d/')[1].split('/')[0] if "file/d/" in url else url.split('id=')[1].split('&')[0]
        direct_url = f"https://drive.google.com/uc?export=download&id={file_id}"
        return requests.get(direct_url, timeout=10).content
    except: return None

@st.dialog("DETALLES")
def comprar_producto(row):
    # (Misma lógica de la ventana anterior para no extender el código)
    st.subheader(row['Nombre'])
    img_data = get_image_from_drive(row["Imagen 1 link de la primera imagen"])
    if img_data: st.image(img_data, use_container_width=True)
    st.write(f"Precio: ${row['Precio']}")
    # Link a WhatsApp...
    tallas = str(row["Tallas"]).split(',')
    talla_sel = st.selectbox("Talla:", tallas)
    if st.button("CONFIRMAR PEDIDO"):
        mensaje = f"Hola Yalis, quiero las {row['Nombre']} en talla {talla_sel}"
        st.markdown(f'<a href="https://wa.me/{WHATSAPP_NUMBER}?text={urllib.parse.quote(mensaje)}" target="_blank">Click aquí para ir a WhatsApp</a>', unsafe_allow_html=True)

# HEADER
st.markdown("<h1 style='text-align:center; font-family:Cinzel; margin-top:-50px;'>YALIS</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#D4AF37; letter-spacing:4px; font-size:0.8rem;'>LUXURY FOOTWEAR</p><br>", unsafe_allow_html=True)

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(ttl="5m").dropna(subset=['Nombre'])

    main_cols = st.columns(3)
    
    for index, row in df.iterrows():
        with main_cols[index % 3]:
            # TODO DENTRO DE ESTE DIV HTML
            st.markdown(f'''
                <div class="product-card">
                    <div class="img-container">
                        <img src="data:image/png;base64,{pd.io.common.base64.b64encode(get_image_from_drive(row["Imagen 1 link de la primera imagen"])).decode() if get_image_from_drive(row["Imagen 1 link de la primera imagen"]) else ""}">
                    </div>
                    <div class="info-container">
                        <div class="product-title">{row['Nombre']}</div>
                        <div class="product-price">${row['Precio']}</div>
                    </div>
                </div>
            ''', unsafe_allow_html=True)
            
            # El botón de Streamlit debe ir justo debajo pero lo integramos visualmente
            if st.button("VER DETALLES", key=f"v_{row['cod.']}"):
                comprar_producto(row)
            st.markdown("<br>", unsafe_allow_html=True)

except Exception as e:
    st.error("Cargando catálogo...")
