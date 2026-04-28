import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import urllib.parse
import requests
from io import BytesIO
import base64

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="YALIS SHOES| Calzado para dama", layout="wide")

WHATSAPP_NUMBER = "593978868363"

# --- CSS INTEGRADO ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;800&display=swap');

.stApp, [data-testid="stDialog"] { 
    background-color: #FFFFFF; 
    font-family: 'Montserrat', sans-serif !important; 
}

div[data-testid="stDialog"] div[role="dialog"] {
    background-color: #FFFFFF !important;
    border-radius: 20px !important;
    max-width: 900px !important;
}

div[data-testid="stDialog"] h3, 
div[data-testid="stDialog"] p, 
div[data-testid="stDialog"] span, 
div[data-testid="stDialog"] label {
    color: #000000 !important;
}

div[data-testid="stVerticalBlockBorderWrapper"] > div {
    border: 2px solid #E91E63 !important;
    border-radius: 25px !important;
    padding: 20px !important;
    background-color: white !important;
    transition: all 0.3s ease-in-out !important;
    height: 100% !important;
    display: flex !important;
    flex-direction: column !important;
}

div[data-testid="stVerticalBlockBorderWrapper"] > div:hover {
    transform: translateY(-5px) !important;
    box-shadow: 0 12px 30px rgba(233, 30, 99, 0.2) !important;
}

.tarjeta-imagen {
    width: 100% !important;
    height: 220px !important;
    object-fit: cover !important;
    border-radius: 15px !important;
    margin-bottom: 10px !important;
}

.product-title {
    color: #E91E63;
    font-weight: 800;
    font-size: 1.4rem;
    text-transform: uppercase;
    text-align: center;
    display: block;
    margin-bottom: -15px !important;
    min-height: 50px !important;
}

.product-price-cat {
    font-weight: 600;
    font-size: 1.3rem;
    color: #333;
}

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

div[data-testid="stTextInput"] input {
    border: 2px solid #E91E63 !important;
    border-radius: 50px !important;
    padding: 10px 20px !important;
    font-family: 'Montserrat', sans-serif !important;
}

div[data-testid="stNumberInput"] input {
    border: 2px solid #E91E63 !important;
    border-radius: 10px !important;
    text-align: center !important;
}

/* Botones de navegación del slider - estilo fucsia */
div[data-testid="stButton"] > button[kind="secondary"] {
    background: #E91E63 !important;
    color: white !important;
    border-radius: 50% !important;
    width: 45px !important;
    height: 45px !important;
    font-size: 18px !important;
    border: none !important;
    min-height: 45px !important;
}

div[data-testid="stButton"] > button[kind="secondary"]:hover {
    background: #C2185B !important;
    color: white !important;
}

/* Miniaturas del slider */
.thumb-container {
    display: flex;
    gap: 8px;
    justify-content: center;
    margin-top: 10px;
}

.thumb-img {
    width: 55px;
    height: 55px;
    object-fit: cover;
    border-radius: 8px;
    cursor: pointer;
    border: 2px solid transparent;
    opacity: 0.5;
    transition: all 0.2s;
}

.thumb-img:hover {
    opacity: 0.8;
}

.thumb-img.active {
    border-color: #E91E63;
    opacity: 1;
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

def img_to_base64(img_bytesio):
    """Convierte BytesIO a base64 string"""
    if img_bytesio is None:
        return None
    img_bytesio.seek(0)
    return base64.b64encode(img_bytesio.getvalue()).decode()

# --- VENTANA EMERGENTE (MODAL) CON SLIDER NATIVO ---
@st.dialog("Detalle del producto")
def comprar_producto(row):
    # NOMBRE EN COLOR FUCSIA
    st.markdown(f"<h2 style='color:#E91E63; font-family:Montserrat; font-weight:800; text-align:center; margin-bottom:20px;'>{row['Nombre']}</h2>", unsafe_allow_html=True)
    
    # Recolectar imágenes disponibles
    imagenes_bytes = []
    nombres_cols = ["Imagen 1 link de la primera imagen", "Imagen 2 link de la segunda imagen", "Imagen 3 link de la tercera imagen"]
    for col_img_name in nombres_cols:
        if col_img_name in row.index and pd.notna(row[col_img_name]):
            img_data = get_image_from_drive(row[col_img_name])
            if img_data:
                imagenes_bytes.append(img_data)
    
    col_img, col_det = st.columns([1.2, 1])
    
    with col_img:
        if len(imagenes_bytes) > 1:
            # SLIDER CON SESSION STATE
            slider_key = f"slider_idx_{row['cod.']}"
            if slider_key not in st.session_state:
                st.session_state[slider_key] = 0
            
            idx_actual = st.session_state[slider_key]
            
            # IMAGEN PRINCIPAL
            st.image(imagenes_bytes[idx_actual], use_container_width=True)
            
            # CONTROLES DE NAVEGACIÓN
            nav_col1, nav_col2, nav_col3 = st.columns([1, 2, 1])
            
            with nav_col1:
                if st.button("◀", key=f"prev_{row['cod.']}", type="secondary"):
                    nuevo_idx = (idx_actual - 1) % len(imagenes_bytes)
                    st.session_state[slider_key] = nuevo_idx
                    st.rerun()
            
            with nav_col2:
                st.markdown(
                    f'<p style="text-align:center; color:#888; font-size:0.9rem; margin-top:8px;">'
                    f'{idx_actual + 1} / {len(imagenes_bytes)}</p>',
                    unsafe_allow_html=True
                )
            
            with nav_col3:
                if st.button("▶", key=f"next_{row['cod.']}", type="secondary"):
                    nuevo_idx = (idx_actual + 1) % len(imagenes_bytes)
                    st.session_state[slider_key] = nuevo_idx
                    st.rerun()
            
            # MINIATURAS COMO HTML (más confiable que botones sobre imágenes)
            thumbs_html = '<div class="thumb-container">'
            for i, img in enumerate(imagenes_bytes):
                img_b64 = img_to_base64(img)
                active_class = "active" if i == idx_actual else ""
                # Usar un botón de Streamlit invisible encima no funciona bien, 
                # así que usamos HTML con JavaScript para cambiar de imagen
                thumbs_html += f'<img src="data:image/jpeg;base64,{img_b64}" class="thumb-img {active_class}">'
            thumbs_html += '</div>'
            st.markdown(thumbs_html, unsafe_allow_html=True)
            
            # Botones debajo de las miniaturas para seleccionar imagen
            thumb_cols = st.columns(len(imagenes_bytes))
            for i, tcol in enumerate(thumb_cols):
                with tcol:
                    if st.button(f"{i+1}", key=f"thumb_btn_{row['cod.']}_{i}", use_container_width=True):
                        st.session_state[slider_key] = i
                        st.rerun()
            
        elif len(imagenes_bytes) == 1:
            st.image(imagenes_bytes[0], use_container_width=True)
        else:
            st.info("Sin imagen disponible")
            
    with col_det:
        # PRECIO Y OTROS TEXTOS EN NEGRO
        st.markdown(f"<h3 style='color:#000000; font-family:Montserrat; font-size:1.8rem;'>${row['Precio']}</h3>", unsafe_allow_html=True)
        st.markdown(f"<p style='color:#000000; font-size:1.1rem;'><b>Colección:</b> {row['Coleccion']}</p>", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        tallas = str(row["Tallas"]).split(',')
        talla_sel = st.selectbox("Selecciona tu talla:", tallas)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # SELECTOR DE CANTIDAD
        cantidad = st.number_input("Cantidad:", min_value=1, max_value=5, value=1, step=1)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        mensaje = f"Hola YALIS, deseo comprar: {row['Nombre']} (x{cantidad}) en talla {talla_sel}"
        wa_url = f"https://wa.me/{WHATSAPP_NUMBER}?text={urllib.parse.quote(mensaje)}"
        
        st.markdown(f'''
            <a href="{wa_url}" target="_blank" style="text-decoration:none;">
                <div style="
                    background-color: #25D366; 
                    color: #000000; 
                    text-align: center; 
                    padding: 15px; 
                    border-radius: 50px; 
                    font-weight: 800; 
                    font-family: Montserrat;
                    font-size: 1.1rem;
                    border: 2px solid #128C7E;
                    transition: all 0.3s;">
                    📱 WHATSAPP
                </div>
            </a>
        ''', unsafe_allow_html=True)

# --- CABECERA ---
st.markdown('<h1 style="text-align:center; color:#E91E63; font-weight:800; margin-bottom:10px;">YALIS SHOES</h1>', unsafe_allow_html=True)

# BUSCADOR DE PRODUCTOS
st.markdown('<div style="max-width:500px; margin:0 auto 30px
