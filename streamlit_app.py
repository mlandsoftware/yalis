import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import urllib.parse
import requests
from io import BytesIO

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="YALIS SHOES| Calzado para dama", layout="wide")

WHATSAPP_NUMBER = "593978868363"

# --- CSS INTEGRADO ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;800&display=swap');

/* Configuración base */
.stApp, [data-testid="stDialog"] { 
    background-color: #FFFFFF; 
    font-family: 'Montserrat', sans-serif !important; 
}

/* ESTILO DEL DIÁLOGO (VENTANA EMERGENTE) */
div[data-testid="stDialog"] div[role="dialog"] {
    background-color: #FFFFFF !important;
    border-radius: 20px !important;
}

/* Forzar negro en textos informativos del modal */
div[data-testid="stDialog"] h3, 
div[data-testid="stDialog"] p, 
div[data-testid="stDialog"] span, 
div[data-testid="stDialog"] label {
    color: #000000 !important;
}

/* TARJETA DEL CATÁLOGO */
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

/* TÍTULOS EN EL CATÁLOGO (FUCSIA) */
.product-title {
    color: #E91E63;
    font-weight: 800;
    font-size: 1.4rem;
    text-transform: uppercase;
    text-align: center;
    display: block;
    margin-bottom: -15px !important;
}

.product-price-cat {
    font-weight: 600;
    font-size: 1.3rem;
    color: #333;
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

/* ESTILO DEL BUSCADOR */
div[data-testid="stTextInput"] input {
    border: 2px solid #E91E63 !important;
    border-radius: 50px !important;
    padding: 10px 20px !important;
    font-family: 'Montserrat', sans-serif !important;
}

/* ESTILO SELECTOR CANTIDAD */
div[data-testid="stNumberInput"] input {
    border: 2px solid #E91E63 !important;
    border-radius: 10px !important;
    text-align: center !important;
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
    # NOMBRE EN COLOR FUCSIA
    st.markdown(f"<h2 style='color:#E91E63; font-family:Montserrat; font-weight:800; text-align:center;'>{row['Nombre']}</h2>", unsafe_allow_html=True)
    
    col_img, col_det = st.columns([1.2, 1])
    
    with col_img:
        # 6. GALERÍA DE IMÁGENES (Imagen 1, 2 y 3 si existen)
        imagenes = []
        for col_img_name in ["Imagen 1 link de la primera imagen", "Imagen 2 link de la segunda imagen", "Imagen 3 link de la tercera imagen"]:
            if col_img_name in row.index and pd.notna(row[col_img_name]):
                img_data = get_image_from_drive(row[col_img_name])
                if img_data:
                    imagenes.append(img_data)
        
        if imagenes:
            if len(imagenes) == 1:
                st.image(imagenes[0], use_container_width=True)
            else:
                # Miniaturas clickeables o grid de imágenes
                st.image(imagenes, use_container_width=True)
        else:
            st.info("Sin imagen disponible")
            
    with col_det:
        # PRECIO Y OTROS TEXTOS EN NEGRO
        st.markdown(f"<h3 style='color:#000000; font-family:Montserrat;'>${row['Precio']}</h3>", unsafe_allow_html=True)
        st.markdown(f"<p style='color:#000000;'><b>Colección:</b> {row['Coleccion']}</p>", unsafe_allow_html=True)
        
        tallas = str(row["Tallas"]).split(',')
        talla_sel = st.selectbox("Selecciona tu talla:", tallas)
        
        # 8. SELECTOR DE CANTIDAD
        cantidad = st.number_input("Cantidad:", min_value=1, max_value=5, value=1, step=1)
        
        mensaje = f"Hola YALIS, deseo comprar: {row['Nombre']} (x{cantidad}) en talla {talla_sel}"
        wa_url = f"https://wa.me/{WHATSAPP_NUMBER}?text={urllib.parse.quote(mensaje)}"
        
        st.markdown(f'''
            <a href="{wa_url}" target="_blank" style="text-decoration:none;">
                <div style="
                    background-color: #25D366; 
                    color: #000000; 
                    text-align: center; 
                    padding: 12px; 
                    border-radius: 50px; 
                    font-weight: 800; 
                    font-family: Montserrat;
                    margin-top: 10px;
                    border: 1px solid #128C7E;">
                    WHATSAPP
                </div>
            </a>
        ''', unsafe_allow_html=True)

# --- CABECERA ---
st.markdown('<h1 style="text-align:center; color:#E91E63; font-weight:800; margin-bottom:10px;">YALIS SHOES</h1>', unsafe_allow_html=True)

# 4. BUSCADOR DE PRODUCTOS
st.markdown('<div style="max-width:500px; margin:0 auto 30px auto;">', unsafe_allow_html=True)
busqueda = st.text_input("", placeholder="🔍 Buscar modelo...", label_visibility="collapsed")
st.markdown('</div>', unsafe_allow_html=True)

# --- CATÁLOGO ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(ttl="5m").dropna(subset=['Nombre'])

    # Filtrar por búsqueda
    if busqueda:
        df = df[df['Nombre'].str.contains(busqueda, case=False, na=False)]
        if df.empty:
            st.info("No se encontraron productos con ese nombre.")
    
    # Verificar columnas de imágenes adicionales
    columnas_imagenes = ["Imagen 1 link de la primera imagen", "Imagen 2 link de la segunda imagen", "Imagen 3 link de la tercera imagen"]
    for col in columnas_imagenes[1:]:
        if col not in df.columns:
            df[col] = None

    main_cols = st.columns(3)
    for index, row in df.iterrows():
        with main_cols[index % 3]:
            with st.container(border=True):
                # 1. NOMBRE
                st.markdown(f'<span class="product-title">{row["Nombre"]}</span>', unsafe_allow_html=True)
                
                # 2. FOTO
                portada = get_image_from_drive(row["Imagen 1 link de la primera imagen"])
                if portada:
                    st.image(portada, use_container_width=True)
                
                # 3. PRECIO Y BOTÓN
                c_pre, c_btn = st.columns([1, 1.2])
                with c_pre:
                    st.markdown(f'<div class="product-price-cat">${row["Precio"]}</div>', unsafe_allow_html=True)
                with c_btn:
                    if st.button("COMPRAR", key=f"btn_{row['cod.']}"):
                        comprar_producto(row)

except Exception as e:
    st.error("Conectando con el inventario...")

# 5. FOOTER CON INFO DE CONTACTO
st.markdown("""
<div style="text-align:center; margin-top:60px; padding:40px 20px; border-top:2px solid #E91E63;">
    <h3 style="color:#E91E63; font-family:Montserrat; font-weight:800; margin-bottom:20px;">YALIS SHOES</h3>
    <p style="color:#333; font-family:Montserrat; font-size:1rem; line-height:1.8;">
        📍 Quito, Ecuador &nbsp;|&nbsp; 📱 +593 97 886 8363<br>
        🚚 Envíos a todo el país &nbsp;|&nbsp; 💳 Pagos contra entrega
    </p>
    <p style="color:#888; font-family:Montserrat; font-size:0.85rem; margin-top:20px;">
        © 2026 YALIS SHOES - Calzado para dama
    </p>
</div>
""", unsafe_allow_html=True)
