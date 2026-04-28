import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import urllib.parse
import requests
from io import BytesIO

# 1. Configuración de página y forzado de tema visual
st.set_page_config(page_title="YALIS | Luxury Footwear", layout="wide")

# WhatsApp Config
WHATSAPP_NUMBER = "593978868363"

# 2. CSS Maestro: Estilo de Lujo, Bordes Suavizados y Responsive
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&family=Montserrat:wght@300;400;600&display=swap');

    /* Forzar fondo y colores independientemente del modo del navegador */
    .stApp {
        background-color: #FFFFFF;
    }
    
    html, body, [data-testid="stAppViewContainer"] {
        color: #1A1A1A !important;
        font-family: 'Montserrat', sans-serif;
    }

    /* Títulos Elegantes */
    h1, h2, h3 {
        font-family: 'Cinzel', serif !important;
        color: #1A1A1A !important;
        text-align: center;
    }

    /* Tarjetas de Producto Suavizadas */
    .product-card {
        background-color: #Fdfdfd;
        border-radius: 20px;
        padding: 15px;
        border: 1px solid #EAEAEA;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin-bottom: 25px;
        transition: transform 0.3s ease;
    }
    .product-card:hover {
        transform: translateY(-5px);
        border-color: #D4AF37;
    }

    /* Botones con Bordes Suaves y Gradiente sutil */
    .stButton>button {
        background: linear-gradient(145deg, #1A1A1A, #333333);
        color: #D4AF37 !important;
        border-radius: 50px !important; /* Bordes muy suaves */
        border: 1px solid #D4AF37 !important;
        padding: 10px 25px !important;
        font-weight: 600;
        letter-spacing: 1px;
        width: 100%;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background: #D4AF37 !important;
        color: #1A1A1A !important;
        box-shadow: 0 5px 15px rgba(212, 175, 55, 0.4);
    }

    /* Ajustes para Móviles */
    @media (max-width: 768px) {
        .stColumns {
            display: block !important;
        }
        div[data-testid="column"] {
            width: 100% !important;
            margin-bottom: 20px !important;
        }
    }

    /* Estilo de los Tabs (Slider) */
    .stTabs [data-baseweb="tab-list"] {
        justify-content: center;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px 10px 0 0;
        color: #888 !important;
    }
    .stTabs [aria-selected="true"] {
        color: #D4AF37 !important;
        border-bottom-color: #D4AF37 !important;
    }

    /* Ocultar elementos innecesarios de Streamlit */
    header {visibility: hidden;}
    footer {visibility: hidden;}
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
@st.dialog("DETALLES DE COLECCIÓN")
def comprar_producto(row):
    st.markdown(f"<h2 style='text-align:left; color:#1A1A1A;'>{row['Nombre']}</h2>", unsafe_allow_html=True)
    
    col_img, col_det = st.columns([1.3, 1])
    
    with col_img:
        img_cols = ["Imagen 1 link de la primera imagen", "Imagen 2 link de la segunda imagen", "Imagen 3 link de la tercera imagen"]
        t1, t2, t3 = st.tabs(["①", "②", "③"])
        for i, t in enumerate([t1, t2, t3]):
            with t:
                data = get_image_from_drive(row[img_cols[i]])
                if data: st.image(data, use_container_width=True, caption=f"Vista {i+1}")

    with col_det:
        st.markdown(f"<p style='color:#888;'>Cod: {row['cod.']}</p>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='text-align:left; color:#D4AF37;'>${row['Precio']}</h3>", unsafe_allow_html=True)
        
        tallas = str(row["Tallas"]).split(',')
        talla_sel = st.selectbox("Talla Americana / Local:", tallas)
        cantidad = st.number_input("Pares:", min_value=1, step=1)
        
        total = float(row["Precio"]) * cantidad
        
        mensaje = f"Hola YALIS, deseo adquirir:\n👠 *{row['Nombre']}*\n📏 Talla: {talla_sel}\n🔢 Cantidad: {cantidad}\n💰 Total: ${total:.2f}"
        wa_url = f"https://wa.me/{WHATSAPP_NUMBER}?text={urllib.parse.quote(mensaje)}"
        
        st.markdown(f"""
            <a href="{wa_url}" target="_blank" style="text-decoration:none;">
                <div style="background:#25D366; color:white; text-align:center; padding:15px; border-radius:50px; font-weight:bold; margin-top:20px; box-shadow: 0 4px 10px rgba(0,0,0,0.1);">
                    SOLICITAR PEDIDO (WHATSAPP)
                </div>
            </a>
            """, unsafe_allow_html=True)

# --- HEADER ---
st.markdown("""
    <div style="text-align:center; padding: 20px 0;">
        <h1 style="font-size: 3em; margin-bottom:0;">YALIS</h1>
        <p style="letter-spacing: 5px; color: #D4AF37; font-weight:300;">LUXURY FOOTWEAR COLLECTION</p>
    </div>
    """, unsafe_allow_html=True)

# --- CONTENIDO ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(ttl="5m").dropna(subset=['Nombre'])

    # Grid de 3 columnas para PC, se ajusta por CSS a 1 para móvil
    main_cols = st.columns(3)
    
    for index, row in df.iterrows():
        with main_cols[index % 3]:
            st.markdown('<div class="product-card">', unsafe_allow_html=True)
            
            portada = get_image_from_drive(row["Imagen 1 link de la primera imagen"])
            if portada:
                st.image(portada, use_container_width=True)
            
            st.markdown(f"<h4>{row['Nombre']}</h4>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center; color:#D4AF37; font-weight:600;'>${row['Precio']}</p>", unsafe_allow_html=True)
            
            if st.button("VER DETALLES", key=f"v_{row['cod.']}"):
                comprar_producto(row)
            
            st.markdown('</div>', unsafe_allow_html=True)

except Exception as e:
    st.error("Sincronizando con el catálogo de lujo...")
