import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import urllib.parse
import requests
from io import BytesIO

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="YALIS | Luxury Footwear", layout="wide")

WHATSAPP_NUMBER = "593978868363"

# --- CSS REFINADO (NOMBRE CENTRADO Y BORDE CONCORDANTE) ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;800&display=swap');

.stApp { background-color: #FFFFFF; font-family: 'Montserrat', sans-serif; }

/* TARJETA: Contenedor principal de Streamlit */
[data-testid="stVerticalBlockBorderWrapper"] {
    border: 2px solid #E91E63 !important; /* Borde fucsia Mary Luna */
    border-radius: 25px !important;
    padding: 20px !important;
    background-color: white !important;
    box-shadow: 0 4px 15px rgba(233, 30, 99, 0.1) !important;
    transition: all 0.3s ease-in-out !important;
}

[data-testid="stVerticalBlockBorderWrapper"]:hover {
    transform: translateY(-5px) !important;
    box-shadow: 0 10px 25px rgba(233, 30, 99, 0.2) !important;
}

/* 1. NOMBRE CENTRADO */
.product-title {
    color: #E91E63;
    font-weight: 800;
    font-size: 1.1rem;
    text-transform: uppercase;
    text-align: center; /* CENTRADO */
    display: block;
    margin-bottom: 15px;
    line-height: 1.2;
    min-height: 45px;
}

/* 2. IMAGEN (Proporción Cuadrada) */
[data-testid="stImage"] img {
    border-radius: 15px !important;
    aspect-ratio: 1 / 1 !important;
    object-fit: cover !important;
    margin: 0 auto !important;
}

/* 3. FILA DE PRECIO Y BOTÓN */
.price-container {
    font-weight: 600;
    font-size: 1.3rem;
    color: #333;
    display: flex;
    align-items: center;
}

/* BOTÓN "COMPRAR" OVALADO */
.stButton > button {
    background: transparent !important;
    color: #E91E63 !important;
    border: 2px solid #E91E63 !important;
    border-radius: 50px !important; /* Estilo ovalado */
    padding: 5px 25px !important;
    font-weight: 700 !important;
    font-size: 0.85rem !important;
    text-transform: uppercase;
    width: 100% !important;
    transition: all 0.3s ease !important;
}

.stButton > button:hover {
    background: #E91E63 !important;
    color: white !important;
}

/* Ajuste para que las columnas internas no tengan margen extra */
[data-testid="column"] {
    display: flex;
    align-items: center;
    justify-content: center;
}

header {visibility: hidden;}
footer {visibility: hidden;}
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

@st.dialog("DETALLES DEL CALZADO")
def comprar_producto(row):
    st.markdown(f"<h2 style='color:#E91E63; text-align:center;'>{row['Nombre']}</h2>", unsafe_allow_html=True)
    col_img, col_det = st.columns([1.2, 1])
    with col_img:
        img_cols = ["Imagen 1 link de la primera imagen", "Imagen 2 link de la segunda imagen", "Imagen 3 link de la tercera imagen"]
        t1, t2, t3 = st.tabs(["Vista 1", "Vista 2", "Vista 3"])
        for i, t in enumerate([t1, t2, t3]):
            with t:
                data = get_image_from_drive(row[img_cols[i]])
                if data: st.image(data, use_container_width=True)
    with col_det:
        st.markdown(f"## ${row['Precio']}")
        st.write(f"**Colección:** {row['Coleccion']}")
        tallas = str(row["Tallas"]).split(',')
        talla_sel = st.selectbox("Selecciona Talla:", tallas)
        cantidad = st.number_input("Pares:", min_value=1, step=1)
        total = float(row["Precio"]) * cantidad
        wa_url = f"https://wa.me/{WHATSAPP_NUMBER}?text=Deseo comprar: {row['Nombre']} (Talla: {talla_sel})"
        st.markdown(f'<a href="{wa_url}" target="_blank" style="text-decoration:none;"><div style="background:#25D366; color:white; text-align:center; padding:12px; border-radius:50px; font-weight:bold; margin-top:20px;">RESERVAR POR WHATSAPP</div></a>', unsafe_allow_html=True)

# --- CABECERA ---
st.markdown('<h1 style="text-align:center; color:#E91E63; font-weight:800; margin-bottom:40px;">YALIS LUXURY</h1>', unsafe_allow_html=True)

# --- CATÁLOGO ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(ttl="5m").dropna(subset=['Nombre'])

    main_cols = st.columns(3)
    for index, row in df.iterrows():
        with main_cols[index % 3]:
            # El contenedor 'border=True' crea la tarjeta fucsia
            with st.container(border=True):
                # 1. NOMBRE (CENTRADO)
                st.markdown(f'<span class="product-title">{row["Nombre"]}</span>', unsafe_allow_html=True)
                
                # 2. FOTO
                portada = get_image_from_drive(row["Imagen 1 link de la primera imagen"])
                if portada:
                    st.image(portada, use_container_width=True)
                
                # 3. PRECIO Y BOTÓN (LADO A LADO)
                # Usamos una proporción de columnas para que se vean juntos
                col_precio, col_boton = st.columns([1, 1.2])
                with col_precio:
                    st.markdown(f'<div class="price-container">${row["Precio"]}</div>', unsafe_allow_html=True)
                with col_boton:
                    if st.button("COMPRAR", key=f"btn_{row['cod.']}"):
                        comprar_producto(row)

except Exception as e:
    st.error("Error al conectar con el catálogo.")
