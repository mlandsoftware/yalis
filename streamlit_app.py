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

# --- CSS MAESTRO (Diseño de Lujo & Responsive) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@500&family=Montserrat:wght@300;400;600&display=swap');

    /* Forzar fondo blanco y texto oscuro (Agnóstico al tema) */
    .stApp { background-color: #FFFFFF; }
    html, body, [data-testid="stAppViewContainer"] {
        color: #1A1A1A !important;
        font-family: 'Montserrat', sans-serif;
    }

    /* Contenedor de la Tarjeta */
    .product-card {
        background-color: #ffffff;
        border-radius: 25px;
        padding: 0px 0px 20px 0px;
        border: 1px solid #f0f0f0;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05);
        margin-bottom: 30px;
        text-align: center;
        overflow: hidden;
        display: flex;
        flex-direction: column;
        height: 100%;
        transition: transform 0.3s ease;
    }
    .product-card:hover { transform: translateY(-5px); }

    /* Info del producto dentro de la tarjeta */
    .product-info { padding: 15px; }
    .product-title {
        font-family: 'Montserrat', sans-serif;
        font-size: 1.1em;
        font-weight: 600;
        color: #1a1a1a;
        margin-bottom: 5px;
        min-height: 50px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .product-price {
        font-family: 'Montserrat', sans-serif;
        font-size: 1.3em;
        color: #D4AF37;
        font-weight: 400;
    }

    /* Botón Streamlit Personalizado */
    .stButton>button {
        background: #1a1a1a !important;
        color: #D4AF37 !important;
        border-radius: 50px !important;
        border: 1px solid #D4AF37 !important;
        padding: 8px 20px !important;
        font-size: 0.8em !important;
        font-weight: 600 !important;
        letter-spacing: 1px;
        width: 85% !important;
        margin: 0 auto !important;
        display: block;
    }
    .stButton>button:hover {
        background: #D4AF37 !important;
        color: #1a1a1a !important;
    }

    /* Slider de Imágenes (Tabs) */
    .stTabs [data-baseweb="tab-list"] { justify-content: center; gap: 20px; }
    .stTabs [data-baseweb="tab"] { color: #888 !important; }
    .stTabs [aria-selected="true"] { color: #D4AF37 !important; border-bottom-color: #D4AF37 !important; }

    /* Ocultar elementos de Streamlit */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Responsive Grid */
    @media (max-width: 768px) {
        [data-testid="column"] { width: 100% !important; flex: 1 1 100% !important; }
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
