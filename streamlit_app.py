import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import urllib.parse
import requests
from io import BytesIO

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="YALIS | Luxury Footwear", layout="wide")

WHATSAPP_NUMBER = "593978868363"

# --- CSS MEJORADO (CONTENEDOR REAL) ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;800&display=swap');

.stApp { background-color: #FFFFFF; font-family: 'Montserrat', sans-serif; }

/* Forzamos que el contenedor de Streamlit se comporte como la tarjeta */
[data-testid="stVerticalBlockBorderWrapper"] {
    border: 1px solid #E91E63 !important;
    border-radius: 20px !important;
    padding: 15px !important;
    background-color: white !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.05) !important;
    transition: transform 0.3s ease !important;
}

[data-testid="stVerticalBlockBorderWrapper"]:hover {
    transform: translateY(-5px) !important;
    box-shadow: 0 8px 20px rgba(233, 30, 99, 0.15) !important;
}

/* 1. NOMBRE */
.product-title {
    color: #E91E63;
    font-weight: 800;
    font-size: 1rem;
    text-transform: uppercase;
    margin-bottom: 10px;
    min-height: 40px;
    display: block;
}

/* 2. IMAGEN (Proporción 1:1) */
[data-testid="stImage"] img {
    border-radius: 12px !important;
    aspect-ratio: 1 / 1 !important;
    object-fit: cover !important;
}

/* 3. CONTENEDOR INFERIOR */
.bottom-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 10px;
}

.product-price {
    font-weight: 600;
    font-size: 1.2rem;
    color: #333;
}

/* BOTÓN OVALADO */
.stButton > button {
    background: transparent !important;
    color: #E91E63 !important;
    border: 1px solid #E91E63 !important;
    border-radius: 30px !important;
    padding: 5px 15px !important;
    font-weight: 600 !important;
    width: auto !important;
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

@st.dialog("DETALLES DEL PRODUCTO")
def comprar_producto(row):
    st.markdown(f"<h2 style='color:#E91E63;'>{row['Nombre']}</h2>", unsafe_allow_html=True)
    col_img, col_det = st.columns([1.2, 1])
    with col_img:
        img_cols = ["Imagen 1 link de la primera imagen", "Imagen 2 link de la segunda imagen", "Imagen 3 link de la tercera imagen"]
        t1, t2, t3 = st.tabs(["Vista 1", "Vista 2", "Vista 3"])
        for i, t in enumerate([t1, t2, t3]):
            with t:
                data = get_image_from_drive(row[img_cols[i]])
                if data: st.image(data, use_container_width=True)
    with col_det:
        st.markdown(f"### ${row['Precio']}")
        tallas = str(row["Tallas"]).split(',')
        talla_sel = st.selectbox("Talla:", tallas)
        cantidad = st.number_input("Cantidad:", min_value=1, step=1)
        total = float(row["Precio"]) * cantidad
        wa_url = f"https://wa.me/{WHATSAPP_NUMBER}?text=Hola YALIS, pedido: {row['Nombre']} Talla: {talla_sel}"
        st.markdown(f'<a href="{wa_url}" target="_blank" style="text-decoration:none;"><div style="background:#25D366; color:white; text-align:center; padding:12px; border-radius:50px; font-weight:bold;">RESERVAR WHATSAPP</div></a>', unsafe_allow_html=True)

# --- CABECERA ---
st.markdown('<h1 style="text-align:center; color:#E91E63;">YALIS LUXURY</h1>', unsafe_allow_html=True)

# --- CATÁLOGO ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(ttl="5m").dropna(subset=['Nombre'])

    main_cols = st.columns(3)
    for index, row in df.iterrows():
        with main_cols[index % 3]:
            # Usamos st.container con border=True para que Streamlit cree la tarjeta real
            with st.container(border=True):
                # 1. NOMBRE
                st.markdown(f'<span class="product-title">{row["Nombre"]}</span>', unsafe_allow_html=True)
                
                # 2. FOTO
                portada = get_image_from_drive(row["Imagen 1 link de la primera imagen"])
                if portada:
                    st.image(portada, use_container_width=True)
                
                # 3. PRECIO Y BOTÓN (Alineados en la misma fila)
                col_p, col_b = st.columns([1, 1])
                with col_p:
                    st.markdown(f'<div class="product-price">${row["Precio"]}</div>', unsafe_allow_html=True)
                with col_b:
                    if st.button("DETALLES", key=f"btn_{row['cod.']}"):
                        comprar_producto(row)

except Exception as e:
    st.error("Error al cargar el inventario.")
