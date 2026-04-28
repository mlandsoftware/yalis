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
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@500;600;700&family=Montserrat:wght@300;400;500;600&display=swap');

/* Fondo general con un sutil tono marfil (más cálido que el blanco puro) */
.stApp {
    background-color: #FBF9F4;
}

html, body, [data-testid="stAppViewContainer"] {
    color: #1A1A1A !important;
    font-family: 'Montserrat', sans-serif;
}

/* ========== TARJETA DE PRODUCTO ========== */
.product-card {
    background: #FFFFFF;
    border-radius: 28px;
    padding: 0 0 24px 0;
    border: 1px solid rgba(212, 175, 55, 0.15);
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.06),
                0 0 0 1px rgba(212, 175, 55, 0.05) inset;
    margin-bottom: 36px;
    text-align: center;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    height: 100%;
    transition: transform 0.35s cubic-bezier(0.25, 0.46, 0.45, 0.94),
                box-shadow 0.35s ease;
}

.product-card:hover {
    transform: translateY(-10px);
    box-shadow: 0 30px 50px rgba(0, 0, 0, 0.12),
                0 0 0 1px rgba(212, 175, 55, 0.3) inset;
}

/* Imagen dentro de la tarjeta: tamaño uniforme y recorte limpio */
.product-card img {
    width: 100%;
    height: 280px;
    object-fit: cover;
    display: block;
    transition: transform 0.6s ease;
}

.product-card:hover img {
    transform: scale(1.04);
}

/* ========== INFORMACIÓN DEL PRODUCTO ========== */
.product-info {
    padding: 20px 18px 10px 18px;
    flex-grow: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
}

.product-title {
    font-family: 'Montserrat', sans-serif;
    font-weight: 600;
    font-size: 1.15rem;
    letter-spacing: 0.3px;
    color: #2B2B2B;
    min-height: 48px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 6px;
    padding: 0 4px;
    line-height: 1.3;
}

.product-price {
    font-family: 'Cinzel', serif;
    font-size: 1.5rem;
    color: #C5A028;
    font-weight: 500;
    letter-spacing: 1px;
    margin: 4px 0 12px 0;
}

/* ========== BOTÓN (Streamlit) ========== */
.stButton > button {
    background: linear-gradient(135deg, #1A1A1A 0%, #2D2D2D 100%) !important;
    color: #D4AF37 !important;
    border-radius: 50px !important;
    border: 1px solid #D4AF37 !important;
    padding: 12px 28px !important;
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    letter-spacing: 2px;
    text-transform: uppercase;
    width: 82% !important;
    margin: 0 auto !important;
    display: block;
    position: relative;
    overflow: hidden;
    box-shadow: 0 4px 12px rgba(212, 175, 55, 0.25);
    transition: all 0.3s ease;
}

.stButton > button:hover {
    background: linear-gradient(135deg, #D4AF37 0%, #C5A028 100%) !important;
    color: #1A1A1A !important;
    border-color: #D4AF37 !important;
    box-shadow: 0 8px 20px rgba(212, 175, 55, 0.5);
    transform: scale(1.02);
}

/* ========== PESTAÑAS DEL DIÁLOGO ========== */
.stTabs [data-baseweb="tab-list"] {
    justify-content: center;
    gap: 32px;
    padding-bottom: 8px;
}

.stTabs [data-baseweb="tab"] {
    color: #888888 !important;
    font-weight: 500;
    letter-spacing: 0.5px;
    transition: color 0.2s ease;
}

.stTabs [aria-selected="true"] {
    color: #D4AF37 !important;
    border-bottom-color: #D4AF37 !important;
}

/* ========== OCULTAR ELEMENTOS DE STREAMLIT ========== */
header {visibility: hidden;}
footer {visibility: hidden;}

/* ========== RESPONSIVE ========== */
@media (max-width: 992px) {
    /* En tablet: 2 columnas */
    [data-testid="column"] {
        width: 50% !important;
        flex: 1 1 50% !important;
    }
}

@media (max-width: 768px) {
    /* En móvil: 1 columna, fuentes más pequeñas */
    [data-testid="column"] {
        width: 100% !important;
        flex: 1 1 100% !important;
    }
    .product-card img {
        height: 230px;
    }
    .product-title {
        font-size: 1rem;
        min-height: 40px;
    }
    .product-price {
        font-size: 1.3rem;
    }
    .stButton > button {
        padding: 10px 24px !important;
        font-size: 0.75rem !important;
    }
}

/* Pequeño ajuste para que el texto del botón no se corte en resoluciones muy pequeñas */
@media (max-width: 480px) {
    .stButton > button {
        letter-spacing: 1px;
        width: 90% !important;
    }
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
