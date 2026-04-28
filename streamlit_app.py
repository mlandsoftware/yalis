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

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;800&display=swap');

/* FONDO CON FORMAS ORGÁNICAS (Inspirado en las ondas púrpuras de la imagen) */
.stApp {
    background-color: #FFFFFF;
    background-image: radial-gradient(circle at 100% 0%, #bd93d8 0%, #ffffff 40%),
                      radial-gradient(circle at 0% 100%, #bd93d8 0%, #ffffff 40%);
    background-attachment: fixed;
}

html, body, [data-testid="stAppViewContainer"] {
    color: #4A4A4A !important;
    font-family: 'Montserrat', sans-serif;
}

/* ========== TARJETA DE PRODUCTO (Limpia y moderna) ========== */
.product-card {
    background: #FFFFFF;
    border-radius: 40px; /* Bordes muy redondeados como en los elementos de la imagen */
    padding: 15px 15px 30px 15px;
    border: 2px solid #F0F0F0;
    margin-bottom: 30px;
    text-align: center;
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    box-shadow: 0 10px 20px rgba(189, 147, 216, 0.1);
}

.product-card:hover {
    transform: scale(1.03);
    border-color: #ff007f; /* Color Fucsia de la imagen */
    box-shadow: 0 15px 30px rgba(255, 0, 127, 0.15);
}

/* Imagen con bordes redondeados suaves */
.product-card img {
    border-radius: 30px;
    margin-bottom: 15px;
    transition: 0.3s;
}

/* ========== TEXTOS ESTILO "ONLINE SHOPPING" ========== */
.product-title {
    font-weight: 800;
    font-size: 1.2rem;
    color: #ff007f; /* Fucsia vibrante */
    text-transform: uppercase;
    margin-top: 10px;
    letter-spacing: -0.5px;
}

.product-price {
    font-weight: 600;
    font-size: 1.4rem;
    color: #5c2d91; /* Púrpura oscuro */
    margin: 5px 0 20px 0;
}

/* ========== BOTONES "GET STARTED" (Estilo Píldora) ========== */
.stButton > button {
    background: transparent !important;
    color: #ff007f !important;
    border: 2px solid #ff007f !important;
    border-radius: 50px !important;
    padding: 10px 30px !important;
    font-weight: 700 !important;
    text-transform: uppercase;
    letter-spacing: 1px;
    transition: all 0.3s ease !important;
    width: 90% !important;
}

.stButton > button:hover {
    background: #ff007f !important;
    color: white !important;
    box-shadow: 0 5px 15px rgba(255, 0, 127, 0.4);
}

/* ========== CABECERA DINÁMICA ========== */
.main-header {
    text-align: left;
    padding: 20px;
}

.brand-name {
    color: #ff007f;
    font-weight: 800;
    font-size: 1.5rem;
}

/* Ocultar elementos de Streamlit */
header {visibility: hidden;}
footer {visibility: hidden;}

/* Adaptabilidad para móviles */
@media (max-width: 768px) {
    .product-card { border-radius: 30px; }
    .product-title { font-size: 1rem; }
}
</style>
""", unsafe_allow_html=True)

# --- LÓGICA DE IMÁGENES GOOGLE DRIVE ---
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

# --- VENTANA DE DETALLES (MODAL) ---
@st.dialog("DETALLES DEL CALZADO")
def comprar_producto(row):
    st.markdown(f"<h2 style='text-align:left; font-family:Cinzel;'>{row['Nombre']}</h2>", unsafe_allow_html=True)
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
        st.markdown(f"<h3 style='text-align:left; color:#D4AF37;'>${row['Precio']}</h3>", unsafe_allow_html=True)
        st.write(f"**Colección:** {row['Coleccion']}")
        if pd.notna(row['Promocion']):
            st.success(f"Oferta: {row['Promocion']}")
        
        tallas = str(row["Tallas"]).split(',')
        talla_sel = st.selectbox("Selecciona tu talla:", tallas)
        cantidad = st.number_input("Cantidad de pares:", min_value=1, step=1)
        
        total = float(row["Precio"]) * cantidad
        mensaje = f"Hola YALIS, deseo un pedido:\n👠 *{row['Nombre']}*\n📏 Talla: {talla_sel}\n🔢 Cantidad: {cantidad}\n💰 Total: ${total:.2f}"
        wa_url = f"https://wa.me/{WHATSAPP_NUMBER}?text={urllib.parse.quote(mensaje)}"
        
        st.markdown(f"""
            <a href="{wa_url}" target="_blank" style="text-decoration:none;">
                <div style="background:#25D366; color:white; text-align:center; padding:15px; border-radius:50px; font-weight:bold; margin-top:20px;">
                    RESERVAR POR WHATSAPP
                </div>
            </a>
            """, unsafe_allow_html=True)

# --- CABECERA ---
st.markdown("""
    <div style="text-align:center; padding: 40px 0 20px 0;">
        <h1 style="font-family:'Cinzel'; font-size: 3.5em; margin-bottom:0;">YALIS</h1>
        <p style="letter-spacing: 8px; color: #D4AF37; font-weight:300; font-size:0.9em;">LUXURY FOOTWEAR</p>
    </div>
    """, unsafe_allow_html=True)

# --- CATÁLOGO ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(ttl="5m").dropna(subset=['Nombre'])

    main_cols = st.columns(3)
    for index, row in df.iterrows():
        with main_cols[index % 3]:
            # Inicio de la tarjeta
            st.markdown('<div class="product-card">', unsafe_allow_html=True)
            
            # Imagen de Portada
            portada = get_image_from_drive(row["Imagen 1 link de la primera imagen"])
            if portada:
                st.image(portada, use_container_width=True)
            
            # Info y Botón
            st.markdown(f"""
                <div class="product-info">
                    <div class="product-title">{row['Nombre']}</div>
                    <div class="product-price">${row['Precio']}</div>
                </div>
            """, unsafe_allow_html=True)
            
            if st.button("VER DETALLES", key=f"btn_{row['cod.']}"):
                comprar_producto(row)
            
            # Cierre de la tarjeta
            st.markdown('</div>', unsafe_allow_html=True)

except Exception as e:
    st.error("Conectando con el inventario...")
