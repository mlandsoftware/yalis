import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import urllib.parse
import requests
from io import BytesIO

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="YALIS | Luxury Footwear", layout="wide")

WHATSAPP_NUMBER = "593978868363"

# --- CSS INTEGRAL (TARJETA + MODAL) ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;800&display=swap');

.stApp { background-color: #FFFFFF; font-family: 'Montserrat', sans-serif; }

/* 1. ESTILO DE LA TARJETA PRINCIPAL */
div[data-testid="stVerticalBlockBorderWrapper"] > div {
    border: 2px solid #E91E63 !important;
    border-radius: 25px !important;
    padding: 20px !important;
    background-color: white !important;
    box-shadow: 0 4px 10px rgba(0,0,0,0.03) !important;
    transition: all 0.3s ease-in-out !important;
}

div[data-testid="stVerticalBlockBorderWrapper"] > div:hover {
    transform: translateY(-5px) !important;
    box-shadow: 0 12px 30px rgba(233, 30, 99, 0.2) !important;
}

.product-title {
    color: #E91E63;
    font-weight: 800;
    font-size: 1.4rem;
    text-transform: uppercase;
    text-align: center;
    display: block;
    margin-bottom: -15px !important;
    line-height: 1.1;
}

[data-testid="stImage"] img {
    border-radius: 15px !important;
    aspect-ratio: 1 / 1 !important;
    object-fit: cover !important;
}

/* 2. ESTILO PARA EL BOTÓN COMPRAR Y WHATSAPP */
.stButton > button {
    background: transparent !important;
    color: #E91E63 !important;
    border: 2px solid #E91E63 !important;
    border-radius: 50px !important;
    padding: 5px 25px !important;
    font-weight: 700 !important;
    text-transform: uppercase;
    width: 100% !important;
    transition: all 0.3s ease !important;
}

.stButton > button:hover {
    background: #E91E63 !important;
    color: white !important;
}

/* 3. ESTILO DE LAS PESTAÑAS (TABS) EN EL MODAL */
.stTabs [data-baseweb="tab-list"] {
    gap: 10px;
}
.stTabs [data-baseweb="tab"] {
    height: 40px;
    background-color: #f8f8f8;
    border-radius: 10px 10px 0px 0px;
    color: #333;
}
.stTabs [aria-selected="true"] {
    background-color: #E91E63 !important;
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

# --- MODAL DE DETALLES CONCORDANTE ---
@st.dialog("DETALLES DEL PRODUCTO")
def comprar_producto(row):
    # Título en fucsia y grande
    st.markdown(f"<h2 style='color:#E91E63; text-align:center; font-weight:800; text-transform:uppercase;'>{row['Nombre']}</h2>", unsafe_allow_html=True)
    
    col_img, col_det = st.columns([1.2, 1])
    
    with col_img:
        # Pestañas para ver las diferentes fotos del producto
        img_cols = ["Imagen 1 link de la primera imagen", "Imagen 2 link de la segunda imagen", "Imagen 3 link de la tercera imagen"]
        t1, t2, t3 = st.tabs(["VISTA 1", "VISTA 2", "VISTA 3"])
        
        for i, tab in enumerate([t1, t2, t3]):
            with tab:
                data = get_image_from_drive(row[img_cols[i]])
                if data:
                    st.image(data, use_container_width=True)
                else:
                    st.info("Imagen no disponible")

    with col_det:
        st.markdown(f"<h1 style='color:#333; margin-top:0;'>${row['Precio']}</h1>", unsafe_allow_html=True)
        st.write(f"**Colección:** {row['Coleccion']}")
        
        # Opciones de compra
        tallas = str(row["Tallas"]).split(',')
        talla_sel = st.selectbox("Selecciona tu Talla:", tallas)
        cantidad = st.number_input("Cantidad:", min_value=1, value=1, step=1)
        
        # Botón de reserva estilo WhatsApp
        total = float(row["Precio"]) * cantidad
        mensaje = f"Hola YALIS, deseo comprar:\n👠 *{row['Nombre']}*\n📏 Talla: {talla_sel}\n🔢 Cantidad: {cantidad}\n💰 Total: ${total:.2f}"
        wa_url = f"https://wa.me/{WHATSAPP_NUMBER}?text={urllib.parse.quote(mensaje)}"
        
        st.markdown(f'''
            <a href="{wa_url}" target="_blank" style="text-decoration:none;">
                <div style="background:#25D366; color:white; text-align:center; padding:15px; border-radius:50px; font-weight:bold; margin-top:20px; font-size:1.1rem; box-shadow: 0 4px 10px rgba(37, 211, 102, 0.3);">
                    PEDIR POR WHATSAPP
                </div>
            </a>
        ''', unsafe_allow_html=True)

# --- CABECERA PRINCIPAL ---
st.markdown('<h1 style="text-align:center; color:#E91E63; font-weight:800; margin-bottom:40px; font-size:3rem;">YALIS LUXURY</h1>', unsafe_allow_html=True)

# --- CARGA DE DATOS Y RENDERIZADO ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(ttl="5m").dropna(subset=['Nombre'])

    main_cols = st.columns(3)
    for index, row in df.iterrows():
        with main_cols[index % 3]:
            with st.container(border=True):
                # 1. Nombre
                st.markdown(f'<span class="product-title">{row["Nombre"]}</span>', unsafe_allow_html=True)
                
                # 2. Imagen
                portada = get_image_from_drive(row["Imagen 1 link de la primera imagen"])
                if portada:
                    st.image(portada, use_container_width=True)
                
                # 3. Fila de Precio y Botón
                c_pre, c_btn = st.columns([1, 1.2])
                with c_pre:
                    st.markdown(f'<div style="font-weight:600; font-size:1.3rem; color:#333; margin-top:5px;">${row["Precio"]}</div>', unsafe_allow_html=True)
                with c_btn:
                    if st.button("COMPRAR", key=f"btn_{row['cod.']}"):
                        comprar_producto(row)

except Exception as e:
    st.error("Conectando con el inventario...")
