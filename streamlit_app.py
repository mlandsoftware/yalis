import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import urllib.parse
import requests
from io import BytesIO

st.set_page_config(page_title="YALIS Boutique", layout="wide")

WHATSAPP_NUMBER = "593978868363"

# CSS para Estética Femenina y Proporciones Correctas
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=Montserrat:wght@300;400;500&display=swap');

    /* Fondo y Base */
    .stApp { background-color: #ffffff; }
    
    /* Contenedor de Tarjeta */
    .product-card {
        background: #fff;
        border-radius: 30px; /* Bordes mucho más suaves */
        padding: 0px 0px 20px 0px;
        border: 1px solid #f2f2f2;
        box-shadow: 0 10px 25px rgba(0,0,0,0.03);
        margin-bottom: 30px;
        text-align: center;
        overflow: hidden; /* Para que la imagen respete el borde redondeado */
        transition: all 0.4s ease;
    }
    
    .product-card:hover {
        box-shadow: 0 15px 35px rgba(212, 175, 55, 0.1);
        transform: translateY(-8px);
    }

    /* Imagen Proporcional */
    .img-container {
        width: 100%;
        height: 320px; /* Altura fija para uniformidad */
        overflow: hidden;
    }
    .img-container img {
        width: 100%;
        height: 100%;
        object-fit: cover; /* Asegura que no se estiren */
    }

    /* Tipografía Femenina */
    .product-title {
        font-family: 'Playfair Display', serif;
        font-size: 1.3rem;
        color: #1a1a1a;
        margin: 15px 10px 5px 10px;
        font-style: italic;
    }
    
    .product-price {
        font-family: 'Montserrat', sans-serif;
        font-size: 1.1rem;
        color: #C5A059; /* Dorado más suave */
        font-weight: 500;
        margin-bottom: 15px;
    }

    /* Botón Rediseñado */
    .stButton>button {
        background: #1a1a1a !important;
        color: #fff !important;
        border-radius: 40px !important;
        border: none !important;
        padding: 8px 30px !important;
        font-family: 'Montserrat', sans-serif;
        font-size: 0.8rem !important;
        letter-spacing: 2px;
        width: 80% !important; /* Más centrado y elegante */
        margin: 0 auto;
        display: block;
    }

    /* Ajuste para Responsive */
    [data-testid="column"] {
        padding: 0 10px !important;
    }

    /* Ocultar basura visual de Streamlit */
    header, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(show_spinner=False)
def get_image_from_drive(url):
    if not isinstance(url, str) or "drive.google.com" not in url: return None
    try:
        file_id = url.split('/d/')[1].split('/')[0] if "file/d/" in url else url.split('id=')[1].split('&')[0]
        direct_url = f"https://drive.google.com/uc?export=download&id={file_id}"
        response = requests.get(direct_url, timeout=10)
        return BytesIO(response.content) if response.status_code == 200 else None
    except: return None

# Título de Tienda
st.markdown("""
    <div style='text-align: center; padding: 40px 0 20px 0;'>
        <h1 style='font-family: "Playfair Display", serif; font-size: 3.5rem; margin:0;'>Yalis</h1>
        <p style='font-family: "Montserrat", sans-serif; letter-spacing: 6px; color: #C5A059; font-size: 0.7rem;'>COLECCIÓN EXCLUSIVA</p>
    </div>
""", unsafe_allow_html=True)

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(ttl="5m").dropna(subset=['Nombre'])

    # Grid Dinámico
    main_cols = st.columns(3)
    
    for index, row in df.iterrows():
        with main_cols[index % 3]:
            # Todo el contenido dentro de un div con estilo de tarjeta
            st.markdown(f"""
                <div class="product-card">
                    <div class="img-container">
            """, unsafe_allow_html=True)
            
            # Imagen
            portada = get_image_from_drive(row["Imagen 1 link de la primera imagen"])
            if portada:
                st.image(portada, use_container_width=True)
            
            st.markdown(f"""
                    </div>
                    <div class="product-title">{row['Nombre']}</div>
                    <div class="product-price">${row['Precio']}</div>
                </div>
            """, unsafe_allow_html=True)
            
            # El botón de Streamlit se coloca justo debajo, pero visualmente parece parte de la tarjeta
            if st.button("DESCUBRIR", key=f"btn_{row['cod.']}"):
                # Aquí llamarías a tu función st.dialog que ya creamos antes
                st.toast(f"Cargando {row['Nombre']}...") 

except Exception as e:
    st.error("Conectando con Boutique...")
