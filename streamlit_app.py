import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import urllib.parse
import requests
from io import BytesIO

# Configuración de página
st.set_page_config(page_title="Yalis - Calzado de Dama", layout="wide")

WHATSAPP_NUMBER = "593978868363"

# Estilo de Lujo
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Lato:wght@300;400&display=swap');
    html, body, [class*="css"] { font-family: 'Lato', sans-serif; }
    h1, h2, h3 { font-family: 'Playfair Display', serif; letter-spacing: 2px; }
    .stButton>button { background-color: #000; color: #fff; border-radius: 0px; width: 100%; border: none; padding: 10px; }
    .stButton>button:hover { background-color: #444; color: #d4af37; }
    </style>
    """, unsafe_allow_html=True)

# Función Maestra para Imágenes de Google Drive
@st.cache_data(show_spinner=False)
def get_image_from_drive(url):
    try:
        # Extraer el ID del archivo
        if "file/d/" in url:
            file_id = url.split('/d/')[1].split('/')[0]
        elif "id=" in url:
            file_id = url.split('id=')[1].split('&')[0]
        else:
            return None
            
        # URL de descarga directa
        direct_url = f"https://drive.google.com/uc?export=download&id={file_id}"
        
        # Descargar el contenido
        response = requests.get(direct_url)
        if response.status_code == 200:
            return BytesIO(response.content)
        return None
    except Exception:
        return None

# Ventana de Compra
@st.dialog("Detalles del Producto")
def comprar_producto(row):
    col_img, col_det = st.columns([1, 1])
    with col_img:
        img_data = get_image_from_drive(row["Imagen 1 link de la primera imagen"])
        if img_data:
            st.image(img_data, use_container_width=True)
        else:
            st.warning("Imagen no disponible momentáneamente.")
    
    with col_det:
        st.subheader(row["Nombre"])
        st.write(f"**Precio:** ${row['Precio']}")
        tallas_disponibles = str(row["Tallas"]).split(',')
        talla_sel = st.selectbox("Selecciona tu talla:", tallas_disponibles)
        cantidad = st.number_input("Cantidad:", min_value=1, value=1)
        
        total = float(row["Precio"]) * cantidad
        st.markdown(f"### Total: ${total:.2f}")
        
        mensaje = f"Hola Yalis, deseo un pedido:\n*Producto:* {row['Nombre']}\n*Talla:* {talla_sel}\n*Cantidad:* {cantidad}\n*Total:* ${total:.2f}"
        whatsapp_url = f"https://wa.me/{WHATSAPP_NUMBER}?text={urllib.parse.quote(mensaje)}"
        
        st.markdown(f'<a href="{whatsapp_url}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; border:none; padding:12px; cursor:pointer; font-weight:bold;">RESERVAR POR WHATSAPP</button></a>', unsafe_allow_html=True)

# Main App
st.markdown("<h1 style='text-align: center;'>YALIS</h1>", unsafe_allow_html=True)

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(ttl="5m").dropna(subset=['Nombre'])

    cols = st.columns(3)
    for index, row in df.iterrows():
        with cols[index % 3]:
            img_data = get_image_from_drive(row["Imagen 1 link de la primera imagen"])
            if img_data:
                st.image(img_data, use_container_width=True)
            else:
                st.error("Error de enlace")
                
            st.markdown(f"### {row['Nombre']}")
            st.write(f"**${row['Precio']}**")
            
            if st.button("Comprar ahora", key=f"btn_{row['cod.']}"):
                comprar_producto(row)
            st.markdown("<br>", unsafe_allow_html=True)

except Exception as e:
    st.error("Error al conectar con Google Sheets.")
