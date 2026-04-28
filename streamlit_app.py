import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import urllib.parse
import requests
from io import BytesIO

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="YALIS SHOES | Calzado para dama", layout="wide")

WHATSAPP_NUMBER = "593978868363"

# --- CSS INTEGRADO (OPTIMIZADO PARA ORDEN Y RESPONSIVE) ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;800&display=swap');

/* Configuración base */
.stApp { 
    background-color: #FFFFFF; 
    font-family: 'Montserrat', sans-serif !important; 
}

/* ESTILO DEL DIÁLOGO (VENTANA EMERGENTE) */
div[data-testid="stDialog"] div[role="dialog"] {
    background-color: #FFFFFF !important;
    border-radius: 20px !important;
}

div[data-testid="stDialog"] h2, 
div[data-testid="stDialog"] h3, 
div[data-testid="stDialog"] p, 
div[data-testid="stDialog"] span, 
div[data-testid="stDialog"] label {
    color: #000000 !important;
}

/* TARJETA DEL CATÁLOGO (ALTURA FIJA Y ORDEN) */
div[data-testid="stVerticalBlockBorderWrapper"] > div {
    border: 2px solid #E91E63 !important;
    border-radius: 25px !important;
    padding: 15px !important;
    background-color: white !important;
    transition: all 0.3s ease-in-out !important;
    height: 520px; /* Altura fija para uniformidad */
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}

div[data-testid="stVerticalBlockBorderWrapper"] > div:hover {
    transform: translateY(-5px) !important;
    box-shadow: 0 12px 30px rgba(233, 30, 99, 0.2) !important;
}

/* CONTROL DE IMAGEN (RESPONSIVE Y RECORTE) */
div[data-testid="stImage"] img {
    object-fit: cover !important; /* Mantiene la proporción sin estirar */
    height: 280px !important;    /* Altura estándar de imagen en catálogo */
    border-radius: 15px;
}

/* TÍTULOS EN EL CATÁLOGO (FUCSIA) */
.product-title {
    color: #E91E63;
    font-weight: 800;
    font-size: 1.2rem;
    text-transform: uppercase;
    text-align: center;
    display: block;
    min-height: 45px; /* Espacio para nombres largos */
    line-height: 1.2;
}

.product-price-cat {
    font-weight: 700;
    font-size: 1.4rem;
    color: #333;
    text-align: center;
    margin: 10px 0;
}

/* BOTÓN COMPRAR EN CATÁLOGO */
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
                    color: white !important; 
                    text-align: center; 
                    padding: 12px; 
                    border-radius: 50px; 
                    font-weight: 800; 
                    font-family: Montserrat;
                    margin-top: 10px;
                    border: 1px solid #128C7E;">
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

    # Grid de 3 columnas (en móviles Streamlit las apilará automáticamente)
    main_cols = st.columns(3)
    
    for index, row in df.iterrows():
        with main_cols[index % 3]:
            with st.container(border=True):
                # 1. NOMBRE
                st.markdown(f'<span class="product-title">{row["Nombre"]}</span>', unsafe_allow_html=True)
                
                # 2. FOTO (Con contenedor para mantener tamaño uniforme)
                portada = get_image_from_drive(row["Imagen 1 link de la primera imagen"])
                if portada:
                    st.image(portada, use_container_width=True)
                else:
                    st.image("https://via.placeholder.com/300x400?text=Cargando...", use_container_width=True)
                
                # 3. PRECIO
                st.markdown(f'<div class="product-price-cat">${row["Precio"]}</div>', unsafe_allow_html=True)
                
                # 4. BOTÓN
                if st.button("DETALLES / COMPRAR", key=f"btn_{row['cod.']}"):
                    comprar_producto(row)

except Exception as e:
    st.error("Conectando con el inventario...")
