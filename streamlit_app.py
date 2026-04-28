import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import urllib.parse
import requests
from io import BytesIO

# Configuración de página
st.set_page_config(page_title="Yalis - Boutique de Calzado", layout="wide")

WHATSAPP_NUMBER = "593978868363"

# Estilo de Lujo Personalizado
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Lato:wght@300;400&display=swap');
    html, body, [class*="css"] { font-family: 'Lato', sans-serif; }
    h1, h2, h3 { font-family: 'Playfair Display', serif; letter-spacing: 2px; }
    
    /* Botones de Lujo */
    .stButton>button { 
        background-color: #000; 
        color: #fff; 
        border-radius: 0px; 
        width: 100%; 
        border: none; 
        padding: 10px;
        text-transform: uppercase;
        font-size: 0.8em;
        letter-spacing: 1px;
    }
    .stButton>button:hover { background-color: #444; color: #d4af37; }
    
    /* Tabs Estilo Slider */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: #f9f9f9;
        border-radius: 0px;
    }
    </style>
    """, unsafe_allow_html=True)

# Función Maestra para Google Drive con Bypass
@st.cache_data(show_spinner=False)
def get_image_from_drive(url):
    if not isinstance(url, str) or "drive.google.com" not in url:
        return None
    try:
        if "file/d/" in url:
            file_id = url.split('/d/')[1].split('/')[0]
        elif "id=" in url:
            file_id = url.split('id=')[1].split('&')[0]
        else:
            return None
        
        direct_url = f"https://drive.google.com/uc?export=download&id={file_id}"
        response = requests.get(direct_url, timeout=10)
        if response.status_code == 200:
            return BytesIO(response.content)
        return None
    except:
        return None

# Ventana de Compra con Slider (Tabs)
@st.dialog("Detalles de Producto")
def comprar_producto(row):
    col_img, col_det = st.columns([1.2, 1])
    
    with col_img:
        # Definimos las 3 columnas de imágenes de tu Excel
        img_cols = [
            "Imagen 1 link de la primera imagen",
            "Imagen 2 link de la segunda imagen", 
            "Imagen 3 link de la tercera imagen"
        ]
        
        # Crear los tabs para el slider
        tab1, tab2, tab3 = st.tabs(["Vista 1", "Vista 2", "Vista 3"])
        
        for i, tab in enumerate([tab1, tab2, tab3]):
            with tab:
                data = get_image_from_drive(row[img_cols[i]])
                if data:
                    st.image(data, use_container_width=True)
                else:
                    st.caption("Imagen no disponible")

    with col_det:
        st.subheader(row["Nombre"])
        st.markdown(f"**Colección:** {row['Coleccion']}")
        st.markdown(f"**Precio:** <h2 style='color:#d4af37;'>${row['Precio']}</h2>", unsafe_allow_html=True)
        
        if pd.notna(row['Promocion']):
            st.info(f"✨ {row['Promocion']}")

        # Configuración de pedido
        tallas = str(row["Tallas"]).split(',')
        talla_sel = st.selectbox("Selecciona tu talla:", tallas)
        cantidad = st.number_input("Cantidad:", min_value=1, value=1)
        
        total = float(row["Precio"]) * cantidad
        
        # WhatsApp Link
        mensaje = f"Hola Yalis, quiero este producto:\n\n*Zapato:* {row['Nombre']}\n*Talla:* {talla_sel}\n*Cantidad:* {cantidad}\n*Total:* ${total:.2f}\n*Código:* {row['cod.']}"
        wa_url = f"https://wa.me/{WHATSAPP_NUMBER}?text={urllib.parse.quote(mensaje)}"
        
        st.markdown(f"""
            <a href="{wa_url}" target="_blank" style="text-decoration:none;">
                <button style="width:100%; background-color:#25D366; color:white; border:none; padding:15px; cursor:pointer; font-weight:bold; letter-spacing:1px;">
                    PEDIR POR WHATSAPP
                </button>
            </a>
            """, unsafe_allow_html=True)

# --- APP PRINCIPAL ---
st.markdown("<h1 style='text-align: center;'>YALIS</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; letter-spacing: 3px; color: #888;'>EXCLUSIVIDAD Y DISEÑO</p>", unsafe_allow_html=True)
st.divider()

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(ttl="5m").dropna(subset=['Nombre'])

    # Grid de catálogo
    cols = st.columns(3)
    for index, row in df.iterrows():
        with cols[index % 3]:
            # Imagen de portada (Imagen 1)
            portada = get_image_from_drive(row["Imagen 1 link de la primera imagen"])
            if portada:
                st.image(portada, use_container_width=True)
            
            st.markdown(f"### {row['Nombre']}")
            st.write(f"**${row['Precio']}**")
            
            if st.button("Explorar", key=f"view_{row['cod.']}"):
                comprar_producto(row)
            st.markdown("<br>", unsafe_allow_html=True)

except Exception as e:
    st.error("Iniciando conexión con el inventario...")
