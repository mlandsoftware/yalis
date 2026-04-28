import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import urllib.parse
import requests
from io import BytesIO

st.set_page_config(page_title="YALIS | Luxury Footwear", layout="wide")

WHATSAPP_NUMBER = "593978868363"

# CSS Optimizado para Proporción y Responsive
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@500;700&family=Montserrat:wght@300;400;600&display=swap');

    .stApp { background-color: #FFFFFF; }
    html, body, [data-testid="stAppViewContainer"] { 
        color: #1A1A1A !important; 
        font-family: 'Montserrat', sans-serif; 
    }

    /* Contenedor de Tarjeta */
    .product-card {
        background-color: #ffffff;
        border-radius: 15px;
        padding: 0px;
        border: 1px solid #f0f0f0;
        margin-bottom: 30px;
        overflow: hidden;
        transition: all 0.3s ease;
        display: flex;
        flex-direction: column;
        height: 100%; /* Mantiene todas las tarjetas iguales */
    }
    
    .product-info {
        padding: 20px;
        text-align: center;
        display: flex;
        flex-direction: column;
        flex-grow: 1;
        justify-content: space-between;
    }

    /* Tipografía */
    h1 { font-family: 'Cinzel', serif !important; font-size: 3.5rem !important; margin-bottom: 0px !important; }
    h4 { font-family: 'Montserrat', sans-serif !important; font-weight: 600 !important; margin: 10px 0 !important; min-height: 50px; }
    .price-tag { color: #D4AF37; font-size: 1.4rem; font-weight: 700; margin-bottom: 15px; }

    /* Botones de Ancho Completo */
    .stButton>button {
        background-color: #1A1A1A !important;
        color: #D4AF37 !important;
        border-radius: 8px !important;
        border: 1px solid #D4AF37 !important;
        padding: 12px !important;
        font-size: 0.9rem !important;
        font-weight: 600 !important;
        width: 100% !important;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #D4AF37 !important;
        color: #1A1A1A !important;
    }

    /* Responsive: 1 columna en móvil, 3 en PC */
    @media (max-width: 768px) {
        [data-testid="column"] { width: 100% !important; flex: 1 1 100% !important; }
        h1 { font-size: 2.5rem !important; }
    }

    header {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(show_spinner=False)
def get_image_from_drive(url):
    if not isinstance(url, str) or "drive.google.com" not in url: return None
    try:
        file_id = url.split('/d/')[1].split('/')[0] if "file/d/" in url else url.split('id=')[1].split('&')[0]
        res = requests.get(f"https://drive.google.com/uc?export=download&id={file_id}", timeout=10)
        return BytesIO(res.content) if res.status_code == 200 else None
    except: return None

@st.dialog("DETALLES")
def comprar_producto(row):
    # (Mantenemos la lógica de imágenes en Tabs aquí igual que la anterior)
    st.markdown(f"## {row['Nombre']}")
    col_img, col_det = st.columns([1, 1])
    with col_img:
        data = get_image_from_drive(row["Imagen 1 link de la primera imagen"])
        if data: st.image(data, use_container_width=True)
    with col_det:
        st.markdown(f"<h2 style='color:#D4AF37;'>${row['Precio']}</h2>", unsafe_allow_html=True)
        talla_sel = st.selectbox("Talla:", str(row["Tallas"]).split(','))
        msg = f"Hola YALIS, quiero las {row['Nombre']} en talla {talla_sel}"
        st.markdown(f'<a href="https://wa.me/{WHATSAPP_NUMBER}?text={urllib.parse.quote(msg)}" target="_blank"><button style="width:100%; background:#25D366; color:white; border:none; padding:15px; border-radius:10px; font-weight:bold; cursor:pointer;">RESERVAR PEDIDO</button></a>', unsafe_allow_html=True)

# UI PRINCIPAL
st.markdown("<h1>YALIS</h1><p style='text-align:center; color:#D4AF37; letter-spacing:4px;'>Ecuador • Luxury Collection</p>", unsafe_allow_html=True)
st.divider()

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(ttl="5m").dropna(subset=['Nombre'])
    
    # Grid Automático
    main_cols = st.columns(3)
    for index, row in df.iterrows():
        with main_cols[index % 3]:
            # Contenedor visual de la tarjeta
            st.markdown('<div class="product-card">', unsafe_allow_html=True)
            portada = get_image_from_drive(row["Imagen 1 link de la primera imagen"])
            if portada:
                st.image(portada, use_container_width=True)
            
            # Bloque de información
            st.markdown(f"""
                <div class="product-info">
                    <h4>{row['Nombre']}</h4>
                    <div class="price-tag">${row['Precio']}</div>
                </div>
            """, unsafe_allow_html=True)
            
            if st.button("VER DETALLES", key=f"v_{row['cod.']}"):
                comprar_producto(row)
            
            st.markdown('</div>', unsafe_allow_html=True)

except Exception as e:
    st.error("Cargando boutique...")
