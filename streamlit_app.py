import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import urllib.parse
import requests
from io import BytesIO

# Configuración Pro
st.set_page_config(page_title="YALIS | Pasión por el Calzado", layout="wide")

WHATSAPP_NUMBER = "593978868363"

# CSS Maestro: Enfoque en Proporción y Rojo Pasión
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&family=Montserrat:wght@300;500;700&display=swap');

    .stApp { background-color: #fcfcfc; }
    
    /* Contenedor de Tarjeta Todo-en-Uno */
    .product-card {
        background-color: white;
        border-radius: 25px;
        padding: 0px 0px 20px 0px; /* Sin padding arriba para que la imagen toque los bordes */
        border: 1px solid #eee;
        box-shadow: 0 10px 25px rgba(0,0,0,0.08);
        margin-bottom: 30px;
        text-align: center;
        overflow: hidden; /* Corta la imagen para que siga el radio de la tarjeta */
        transition: all 0.3s ease;
        height: 100%;
    }
    
    .product-card:hover {
        transform: translateY(-10px);
        box-shadow: 0 15px 35px rgba(186, 26, 26, 0.2);
        border-color: #BA1A1A;
    }

    /* Ajuste de Imagen Proporcional */
    .product-img-container {
        width: 100%;
        height: 320px;
        overflow: hidden;
    }
    .product-img-container img {
        width: 100%;
        height: 100%;
        object-fit: cover; /* Evita que la imagen se estire */
    }

    /* Tipografía y Colores */
    h1 { font-family: 'Cinzel', serif; color: #BA1A1A !important; font-size: 3.5rem !important; margin-bottom: 0px; }
    h4 { font-family: 'Montserrat', sans-serif; font-weight: 700; color: #1a1a1a; margin: 15px 10px 5px 10px; min-height: 50px; }
    .price-tag { color: #BA1A1A; font-family: 'Montserrat', sans-serif; font-size: 1.4rem; font-weight: 700; margin-bottom: 15px; }

    /* Botón Rojo Pasión con Bordes Suaves */
    .stButton>button {
        background: linear-gradient(145deg, #BA1A1A, #800000) !important;
        color: white !important;
        border-radius: 50px !important;
        border: none !important;
        padding: 12px 30px !important;
        font-family: 'Montserrat', sans-serif;
        font-weight: 600;
        width: 80% !important;
        margin: 0 auto;
        display: block;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background: #000000 !important;
        color: #D4AF37 !important;
        transform: scale(1.05);
    }

    /* Ocultar elementos de Streamlit */
    header, footer { visibility: hidden; }
    
    /* Responsive Grid */
    [data-testid="column"] {
        display: flex;
        flex-direction: column;
        align-items: center;
    }
    </style>
    """, unsafe_allow_html=True)

# Lógica de carga de imágenes
@st.cache_data(show_spinner=False)
def get_image_from_drive(url):
    if not isinstance(url, str) or "drive.google.com" not in url:
        return None
    try:
        file_id = url.split('/d/')[1].split('/')[0] if "file/d/" in url else url.split('id=')[1].split('&')[0]
        direct_url = f"https://drive.google.com/uc?export=download&id={file_id}"
        response = requests.get(direct_url, timeout=10)
        return BytesIO(response.content) if response.status_code == 200 else None
    except:
        return None

# Modal de Detalles con Estilo
@st.dialog("RESERVACIÓN EXCLUSIVA")
def comprar_producto(row):
    col_img, col_det = st.columns([1, 1])
    with col_img:
        img_data = get_image_from_drive(row["Imagen 1 link de la primera imagen"])
        if img_data: st.image(img_data, use_container_width=True)
    with col_det:
        st.markdown(f"## {row['Nombre']}")
        st.markdown(f"<h3 style='color:#BA1A1A;'>${row['Precio']}</h3>", unsafe_allow_html=True)
        tallas = str(row["Tallas"]).split(',')
        talla_sel = st.selectbox("Talla:", tallas)
        cant = st.number_input("Cantidad:", min_value=1, step=1)
        
        total = float(row["Precio"]) * cant
        mensaje = f"Hola YALIS, deseo:\n👠 *{row['Nombre']}*\n📏 Talla: {talla_sel}\n🔢 Cantidad: {cant}\n💰 Total: ${total:.2f}"
        wa_url = f"https://wa.me/{WHATSAPP_NUMBER}?text={urllib.parse.quote(mensaje)}"
        
        st.markdown(f'<a href="{wa_url}" target="_blank" style="text-decoration:none;"><div style="background:#25D366; color:white; text-align:center; padding:15px; border-radius:50px; font-weight:bold;">PEDIR POR WHATSAPP</div></a>', unsafe_allow_html=True)

# --- UI PRINCIPAL ---
st.markdown("<h1>YALIS</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; letter-spacing:8px; color:#888; margin-bottom:40px;'>PASIÓN POR LA ELEGANCIA</p>", unsafe_allow_html=True)

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(ttl="5m").dropna(subset=['Nombre'])

    # Grid Responsive Automático
    main_cols = st.columns(3)
    
    for index, row in df.iterrows():
        with main_cols[index % 3]:
            # Contenedor de Tarjeta
            st.markdown('<div class="product-card">', unsafe_allow_html=True)
            
            # Imagen con Proporción Controlada
            portada = get_image_from_drive(row["Imagen 1 link de la primera imagen"])
            if portada:
                st.image(portada, use_container_width=True)
            
            # Info del Producto
            st.markdown(f"<h4>{row['Nombre']}</h4>", unsafe_allow_html=True)
            st.markdown(f'<p class="price-tag">${row["Precio"]}</p>', unsafe_allow_html=True)
            
            # Botón dentro de la tarjeta
            if st.button("VER DETALLES", key=f"v_{row['cod.']}"):
                comprar_producto(row)
            
            st.markdown('</div>', unsafe_allow_html=True)

except Exception as e:
    st.error("Conectando con la boutique...")
