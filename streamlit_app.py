import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import urllib.parse
import requests
from io import BytesIO

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="YALIS | Luxury Footwear", layout="wide")

WHATSAPP_NUMBER = "593978868363"

# --- CSS REFINADO ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;800&display=swap');

.stApp { background-color: #FFFFFF; font-family: 'Montserrat', sans-serif; }

/* TARJETA PRINCIPAL */
div[data-testid="stVerticalBlockBorderWrapper"] > div {
    border: 2px solid #E91E63 !important;
    border-radius: 25px !important;
    padding: 20px !important;
    background-color: white !important;
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
}

[data-testid="stImage"] img {
    border-radius: 15px !important;
    aspect-ratio: 1 / 1 !important;
    object-fit: cover !important;
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
}

.stButton > button:hover {
    background: #E91E63 !important;
    color: white !important;
}

/* ESTILO PARA LOS BOTONES DE TALLA EN EL MODAL */
div[data-testid="stHorizontalBlock"] button[kind="secondary"] {
    border: 1px solid #ddd !important;
    border-radius: 10px !important;
    padding: 10px !important;
    width: 100% !important;
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

# --- MODAL DE COMPRA MEJORADO ---
@st.dialog("FINALIZAR COMPRA")
def comprar_producto(row):
    # Encabezado del Modal
    st.markdown(f"<h2 style='color:#E91E63; text-align:center; margin-bottom:0;'>{row['Nombre']}</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center; color:gray;'>Colección: {row.get('Coleccion', 'YALIS')}</p>", unsafe_allow_html=True)
    
    col_img, col_det = st.columns([1.1, 1])
    
    with col_img:
        data = get_image_from_drive(row["Imagen 1 link de la primera imagen"])
        if data:
            st.image(data, use_container_width=True)
    
    with col_det:
        st.markdown(f"<h1 style='color:#333; margin-top:0;'>${row['Precio']}</h1>", unsafe_allow_html=True)
        
        # Selección de Tallas con Botones (Segmented Control)
        st.markdown("<b>Selecciona tu Talla:</b>", unsafe_allow_html=True)
        tallas_list = [t.strip() for t in str(row["Tallas"]).split(',')]
        
        # Usamos segmented_control para un diseño moderno de botones
        talla_seleccionada = st.segmented_control(
            "Tallas disponibles", 
            options=tallas_list, 
            label_visibility="collapsed",
            selection_mode="single",
            key=f"talla_{row['cod.']}"
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        cantidad = st.number_input("Cantidad de pares:", min_value=1, value=1, step=1)
        
        if not talla_seleccionada:
            st.warning("Por favor, selecciona una talla.")
            btn_disabled = True
        else:
            btn_disabled = False

        # Botón de WhatsApp estilizado
        total = float(row["Precio"]) * cantidad
        mensaje = f"Hola YALIS, deseo comprar:\n👠 *{row['Nombre']}*\n📏 Talla: {talla_seleccionada}\n🔢 Cantidad: {cantidad}\n💰 Total: ${total:.2f}"
        wa_url = f"https://wa.me/{WHATSAPP_NUMBER}?text={urllib.parse.quote(mensaje)}"
        
        if st.markdown(f'''
            <a href="{wa_url}" target="_blank" style="text-decoration:none;">
                <div style="background:#25D366; color:white; text-align:center; padding:15px; border-radius:50px; font-weight:bold; font-size:1.1rem; margin-top:20px; box-shadow: 0 4px 10px rgba(37, 211, 102, 0.3);">
                    PEDIR POR WHATSAPP
                </div>
            </a>
        ''', unsafe_allow_html=True):
            pass

# --- CABECERA ---
st.markdown('<h1 style="text-align:center; color:#E91E63; font-weight:800; margin-bottom:40px;">YALIS LUJO</h1>', unsafe_allow_html=True)

# --- CATÁLOGO ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(ttl="5m").dropna(subset=['Nombre'])

    main_cols = st.columns(3)
    for index, row in df.iterrows():
        with main_cols[index % 3]:
            with st.container(border=True):
                st.markdown(f'<span class="product-title">{row["Nombre"]}</span>', unsafe_allow_html=True)
                
                portada = get_image_from_drive(row["Imagen 1 link de la primera imagen"])
                if portada:
                    st.image(portada, use_container_width=True)
                
                c_pre, c_btn = st.columns([1, 1.2])
                with c_pre:
                    st.markdown(f'<div style="font-weight:600; font-size:1.3rem; margin-top:10px;">${row["Precio"]}</div>', unsafe_allow_html=True)
                with c_btn:
                    if st.button("COMPRAR", key=f"btn_{row['cod.']}"):
                        comprar_producto(row)

except Exception as e:
    st.error("Error al cargar datos del catálogo.")
