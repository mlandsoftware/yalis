import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import urllib.parse
import requests
from io import BytesIO

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="YALIS SHOES | Calzado para dama", layout="wide")

WHATSAPP_NUMBER = "593978868363"

# --- CSS INTEGRADO PARA ORDEN Y RESPONSIVE ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;800&display=swap');

/* Configuración base */
.stApp { 
    background-color: #FFFFFF; 
    font-family: 'Montserrat', sans-serif !important; 
}

/* FORZAR ORDEN EN LAS TARJETAS (GRID) */
[data-testid="stVerticalBlockBorderWrapper"] > div {
    border: 2px solid #E91E63 !important;
    border-radius: 20px !important;
    padding: 15px !important;
    background-color: white !important;
    height: 520px; /* Altura fija para que todas las tarjetas sean iguales */
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    transition: all 0.3s ease-in-out;
}

[data-testid="stVerticalBlockBorderWrapper"] > div:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 25px rgba(233, 30, 99, 0.2);
}

/* AJUSTE DE IMAGEN PARA QUE NO SE DESCOORDINE */
div[data-testid="stImage"] img {
    object-fit: cover; /* Recorta la imagen para llenar el espacio sin deformarse */
    height: 280px !important; /* Altura fija para todas las fotos del catálogo */
    border-radius: 12px;
}

/* TÍTULOS SIEMPRE ALINEADOS */
.product-title {
    color: #E91E63;
    font-weight: 800;
    font-size: 1.2rem;
    text-transform: uppercase;
    text-align: center;
    display: block;
    min-height: 45px; /* Espacio reservado para el texto */
    line-height: 1.2;
}

.product-price-cat {
    font-weight: 700;
    font-size: 1.4rem;
    color: #333;
    text-align: center;
    margin-top: 5px;
}

/* ESTILO DEL BOTÓN COMPRAR */
.stButton > button {
    background: white !important;
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

/* OCULTAR ELEMENTOS DE STREAMLIT */
header, footer {visibility: hidden;}

/* AJUSTE PARA MÓVILES (Fuentes un poco más pequeñas) */
@media (max-width: 640px) {
    [data-testid="stVerticalBlockBorderWrapper"] > div {
        height: 480px;
    }
    div[data-testid="stImage"] img {
        height: 220px !important;
    }
}
</style>
""", unsafe_allow_html=True)

# --- LÓGICA DE IMÁGENES ---
@st.cache_data(show_spinner=False)
def get_image_from_drive(url):
    if not isinstance(url, str) or "drive.google.com" not in url: 
        return "https://via.placeholder.com/400x500?text=Imagen+No+Disponible"
    try:
        file_id = url.split('/d/')[1].split('/')[0] if "file/d/" in url else url.split('id=')[1].split('&')[0]
        direct_url = f"https://drive.google.com/uc?export=download&id={file_id}"
        response = requests.get(direct_url, timeout=10)
        return BytesIO(response.content) if response.status_code == 200 else None
    except: 
        return None

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
        st.markdown(f"<p style='color:#333;'><b>Colección:</b> {row['Coleccion']}</p>", unsafe_allow_html=True)
        
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
                    padding: 15px; 
                    border-radius: 50px; 
                    font-weight: 800; 
                    font-family: Montserrat;
                    margin-top: 10px;
                    box-shadow: 0 4px 10px rgba(0,0,0,0.1);">
                    PEDIR POR WHATSAPP
                </div>
            </a>
        ''', unsafe_allow_html=True)

# --- HEADER ---
st.markdown('<h1 style="text-align:center; color:#E91E63; font-weight:800; margin-bottom:10px;">YALIS SHOES</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align:center; color:#666; margin-bottom:40px;">Calzado exclusivo para dama</p>', unsafe_allow_html=True)

# --- CATÁLOGO ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    # ttl=0 para desarrollo, cámbialo a "5m" para producción
    df = conn.read(ttl="5m").dropna(subset=['Nombre'])

    # Grid de 3 columnas para PC / Se apila solo en móvil
    main_cols = st.columns(3)
    
    for index, row in df.iterrows():
        # Distribuir productos en las 3 columnas
        with main_cols[index % 3]:
            with st.container(border=True):
                # 1. Nombre
                st.markdown(f'<span class="product-title">{row["Nombre"]}</span>', unsafe_allow_html=True)
                
                # 2. Foto con altura controlada
                portada = get_image_from_drive(row["Imagen 1 link de la primera imagen"])
                st.image(portada, use_container_width=True)
                
                # 3. Precio
                st.markdown(f'<div class="product-price-cat">${row["Precio"]}</div>', unsafe_allow_html=True)
                
                # 4. Botón comprar
                # Usamos el código del producto para que el ID sea único
                if st.button("VER DETALLE", key=f"btn_{row['cod.']}"):
                    comprar_producto(row)

except Exception as e:
    st.error("Conectando con el inventario...")
    st.info("Asegúrate de que la hoja de cálculo sea pública o las credenciales sean correctas.")
