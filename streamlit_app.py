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
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600&display=swap');

/* FONDO DEGRADADO SEGÚN LA IMAGEN */
.stApp {
    background: linear-gradient(135deg, #d4f3ef 0%, #e8f0ff 50%, #fdf2f8 100%);
    font-family: 'Montserrat', sans-serif;
}

/* TARJETA CON ESTILO DE LA IMAGEN (BORDE CURVO ASIMÉTRICO) */
.product-card {
    background: #FFFFFF;
    /* El truco del diseño: bordes redondeados solo en esquinas opuestas */
    border-radius: 0px 80px 0px 80px; 
    padding: 25px;
    margin-bottom: 40px;
    text-align: center;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.05);
    transition: all 0.4s ease;
    border: none;
    display: flex;
    flex-direction: column;
    align-items: center;
}

.product-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
}

/* IMAGEN DENTRO DE LA TARJETA */
.product-card img {
    width: 100%;
    border-radius: 0px 60px 0px 60px; /* Sigue el patrón de la tarjeta */
    object-fit: cover;
    height: 250px;
    margin-bottom: 20px;
}

/* TÍTULOS Y TEXTO */
.product-title {
    font-weight: 600;
    font-size: 1.2rem;
    color: #333;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 10px;
}

.product-price {
    font-weight: 300;
    font-size: 1.1rem;
    color: #666;
    margin-bottom: 20px;
}

/* BOTÓN REDONDEADO "COMPRA TODO" ESTILO IMAGEN */
.stButton > button {
    background-color: #bee3e9 !important; /* Color celeste pastel del botón de la imagen */
    color: #1a1a1a !important;
    border: none !important;
    border-radius: 50px !important; /* Completamente redondeado */
    padding: 10px 40px !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    text-transform: none !important;
    box-shadow: 0 4px 15px rgba(0,0,0,0.05) !important;
    transition: all 0.3s ease !important;
    width: auto !important;
    margin: 0 auto !important;
    display: block;
}

.stButton > button:hover {
    background-color: #a8dadc !important;
    transform: scale(1.05);
}

/* OCULTAR ELEMENTOS INNECESARIOS */
header, footer {visibility: hidden;}

/* AJUSTES DE COLUMNAS */
[data-testid="column"] {
    padding: 1rem !important;
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
