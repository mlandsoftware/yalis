import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import urllib.parse
import requests
from io import BytesIO
import base64

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="YALIS | Luxury Footwear", layout="wide")

WHATSAPP_NUMBER = "593978868363"

# --- DISEÑO CSS ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;800&display=swap');

.stApp { background-color: #FFFFFF; font-family: 'Montserrat', sans-serif; }

/* LA TARJETA CONTENEDORA */
.product-card {
    background: #FFFFFF;
    border: 1px solid #E91E63;
    border-radius: 20px;
    padding: 20px;
    margin-bottom: 10px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    display: flex;
    flex-direction: column;
}

.product-title {
    color: #E91E63;
    font-weight: 800;
    font-size: 1rem;
    text-transform: uppercase;
    margin-bottom: 12px;
    min-height: 40px;
}

.img-container {
    width: 100%;
    aspect-ratio: 1 / 1;
    border-radius: 12px;
    overflow: hidden;
    margin-bottom: 12px;
}

.img-container img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.bottom-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 10px;
}

.product-price {
    font-weight: 600;
    font-size: 1.2rem;
    color: #333;
}

/* Estilo del botón de Streamlit para que encaje en la fila */
.stButton > button {
    background: transparent !important;
    color: #E91E63 !important;
    border: 1px solid #E91E63 !important;
    border-radius: 30px !important;
    padding: 2px 15px !important;
    font-size: 0.75rem !important;
    text-transform: uppercase;
}

.stButton > button:hover {
    background: #E91E63 !important;
    color: white !important;
}

header, footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- FUNCIONES AUXILIARES ---
def get_image_base64(url):
    """Convierte la imagen a base64 para que el HTML la renderice dentro del div"""
    if not isinstance(url, str) or "drive.google.com" not in url:
        return ""
    try:
        file_id = url.split('/d/')[1].split('/')[0] if "file/d/" in url else url.split('id=')[1].split('&')[0]
        direct_url = f"https://drive.google.com/uc?export=download&id={file_id}"
        response = requests.get(direct_url, timeout=10)
        if response.status_code == 200:
            return base64.b64encode(response.content).decode()
    except:
        return ""
    return ""

@st.dialog("DETALLES DEL PRODUCTO")
def comprar_producto(row):
    st.markdown(f"<h2 style='color:#E91E63;'>{row['Nombre']}</h2>", unsafe_allow_html=True)
    st.write(f"### Precio: ${row['Precio']}")
    st.write(f"Colección: {row['Coleccion']}")
    # (Aquí puedes añadir el selector de tallas y el botón de WhatsApp como tenías antes)

# --- CATÁLOGO ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(ttl="5m").dropna(subset=['Nombre'])

    main_cols = st.columns(3)
    for index, row in df.iterrows():
        with main_cols[index % 3]:
            # Obtenemos la imagen en base64 para insertarla directamente en el HTML
            img_b64 = get_image_base64(row["Imagen 1 link de la primera imagen"])
            img_html = f'data:image/jpeg;base64,{img_b64}' if img_b64 else ""

            # Renderizamos toda la tarjeta en un solo bloque HTML
            st.markdown(f"""
                <div class="product-card">
                    <div class="product-title">{row['Nombre']}</div>
                    <div class="img-container">
                        <img src="{img_html}" alt="Calzado">
                    </div>
                    <div class="bottom-row">
                        <div class="product-price">${row['Precio']}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # El botón se pone justo debajo, pero el CSS hará que parezca parte de la tarjeta
            # o podemos usar un truco de margen negativo para subirlo
            st.markdown('<div style="margin-top: -55px; margin-left: 120px; position: relative; z-index: 99;">', unsafe_allow_html=True)
            if st.button("VER", key=f"btn_{row['cod.']}"):
                comprar_producto(row)
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('<br>', unsafe_allow_html=True)

except Exception as e:
    st.error("Conectando...")
