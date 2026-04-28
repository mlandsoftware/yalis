import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import urllib.parse
import requests
from io import BytesIO

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="YALIS | Luxury Footwear", layout="wide")

# WhatsApp Config (Ecuador)
WHATSAPP_NUMBER = "593978868363"

# --- DISEÑO CSS INSPIRADO EN LA IMAGEN ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;800&display=swap');

/* Fondo general */
.stApp {
    background-color: #FFFFFF;
    font-family: 'Montserrat', sans-serif;
}

/* ========== TARJETA DE PRODUCTO ========== */
.product-card {
    background: #FFFFFF;
    border: 1px solid #E91E63; /* Borde fucsia delgado como la imagen */
    border-radius: 20px;
    padding: 20px;
    margin-bottom: 25px;
    display: flex;
    flex-direction: column;
    height: 100%;
    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    transition: transform 0.3s ease;
}

.product-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 20px rgba(233, 30, 99, 0.15);
}

/* 1. NOMBRE (Estilo Mary Luna) */
.product-title {
    color: #E91E63;
    font-weight: 800;
    font-size: 1rem;
    text-transform: uppercase;
    margin-bottom: 15px;
    text-align: left;
    min-height: 45px;
    line-height: 1.2;
}

/* 2. CONTENEDOR DE FOTO (Mantiene proporción) */
.product-image-container {
    width: 100%;
    border-radius: 12px;
    overflow: hidden;
    margin-bottom: 15px;
}

/* Forzar proporción cuadrada para evitar que se estire */
.product-image-container img {
    width: 100%;
    aspect-ratio: 1 / 1; 
    object-fit: cover;
    display: block;
}

/* 3. CONTENEDOR PRECIO Y BOTÓN (Alineados abajo) */
.price-button-container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: auto; /* Empuja al final */
    padding-top: 10px;
}

.product-price {
    font-weight: 600;
    font-size: 1.2rem;
    color: #333;
}

/* BOTÓN OVALADO FUCSIA */
.stButton > button {
    background: transparent !important;
    color: #E91E63 !important;
    border: 1px solid #E91E63 !important;
    border-radius: 30px !important;
    padding: 6px 18px !important;
    font-size: 0.75rem !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    transition: all 0.3s ease !important;
    width: auto !important;
}

.stButton > button:hover {
    background: #E91E63 !important;
    color: white !important;
}

/* OCULTAR ELEMENTOS STREAMLIT */
header {visibility: hidden;}
footer {visibility: hidden;}

/* Responsive */
@media (max-width: 768px) {
    [data-testid="column"] { width: 100% !important; flex: 1 1 100% !important; }
}
</style>
""", unsafe_allow_html=True)

# --- LÓGICA DE IMÁGENES ---
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

# --- MODAL DE DETALLES ---
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
                else: st.caption("Imagen no disponible")

    with col_det:
        st.markdown(f"### ${row['Precio']}")
        st.write(f"**Colección:** {row['Coleccion']}")
        tallas = str(row["Tallas"]).split(',')
        talla_sel = st.selectbox("Talla:", tallas)
        cantidad = st.number_input("Cantidad:", min_value=1, step=1)
        
        total = float(row["Precio"]) * cantidad
        mensaje = f"Hola YALIS, pedido:\n👠 *{row['Nombre']}*\n📏 Talla: {talla_sel}\n🔢 Cantidad: {cantidad}\n💰 Total: ${total:.2f}"
        wa_url = f"https://wa.me/{WHATSAPP_NUMBER}?text={urllib.parse.quote(mensaje)}"
        
        st.markdown(f'<a href="{wa_url}" target="_blank" style="text-decoration:none;"><div style="background:#25D366; color:white; text-align:center; padding:12px; border-radius:50px; font-weight:bold; margin-top:10px;">RESERVAR WHATSAPP</div></a>', unsafe_allow_html=True)

# --- CABECERA ---
st.markdown('<div style="text-align:center; padding: 20px;"><h1 style="color:#E91E63; font-weight:800;">YALIS LUXURY</h1></div>', unsafe_allow_html=True)

# --- CATÁLOGO ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(ttl="5m").dropna(subset=['Nombre'])

    main_cols = st.columns(3)
    for index, row in df.iterrows():
        with main_cols[index % 3]:
            # Apertura de Tarjeta
            st.markdown('<div class="product-card">', unsafe_allow_html=True)
            
            # 1. NOMBRE
            st.markdown(f'<div class="product-title">{row["Nombre"]}</div>', unsafe_allow_html=True)
            
            # 2. FOTO
            portada = get_image_from_drive(row["Imagen 1 link de la primera imagen"])
            st.markdown('<div class="product-image-container">', unsafe_allow_html=True)
            if portada:
                st.image(portada, use_container_width=True)
            else:
                st.write("Imagen no disponible")
            st.markdown('</div>', unsafe_allow_html=True)
            
            # 3. PRECIO Y BOTÓN
            st.markdown('<div class="price-button-container">', unsafe_allow_html=True)
            st.markdown(f'<div class="product-price">${row["Precio"]}</div>', unsafe_allow_html=True)
            
            if st.button("VER DETALLES", key=f"btn_{row['cod.']}"):
                comprar_producto(row)
            
            st.markdown('</div>', unsafe_allow_html=True) # Cierre precio-boton
            st.markdown('</div>', unsafe_allow_html=True) # Cierre tarjeta

except Exception as e:
    st.error("Cargando catálogo...")
