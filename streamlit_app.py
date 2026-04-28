import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import urllib.parse

# Configuración de página
st.set_page_config(page_title="Yalis - Calzado de Dama", layout="wide")

# WhatsApp Config
WHATSAPP_NUMBER = "593978868363"

# Estilo de Lujo (CSS)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Lato:wght@300;400&display=swap');
    html, body, [class*="css"] { font-family: 'Lato', sans-serif; }
    h1, h2, h3 { font-family: 'Playfair Display', serif; letter-spacing: 2px; }
    .stButton>button { background-color: #000; color: #fff; border-radius: 0px; width: 100%; border: none; }
    .stButton>button:hover { background-color: #444; color: #d4af37; }
    .promo-tag { color: #d4af37; font-weight: bold; font-size: 0.9em; }
    div[data-testid="stDialog"] { border-radius: 0px; }
    </style>
    """, unsafe_allow_html=True)

def fix_drive_link(link):
    if "drive.google.com" in link:
        try:
            file_id = link.split('/')[-2]
            return f"https://drive.google.com/uc?export=view&id={file_id}"
        except: return link
    return link

# Ventana de Compra (Dialog)
@st.dialog("Detalles del Producto")
def comprar_producto(row):
    col_img, col_det = st.columns([1, 1])
    
    with col_img:
        st.image(fix_drive_link(row["Imagen 1 link de la primera imagen"]), use_container_width=True)
    
    with col_det:
        st.subheader(row["Nombre"])
        st.write(f"**Precio:** ${row['Precio']}")
        st.write(f"**Colección:** {row['Coleccion']}")
        
        # Opciones de compra
        tallas_disponibles = str(row["Tallas"]).split(',')
        talla_sel = st.selectbox("Selecciona tu talla:", tallas_disponibles)
        cantidad = st.number_input("Cantidad:", min_value=1, max_value=10, value=1)
        
        total = float(row["Precio"]) * cantidad
        st.markdown(f"### Total: ${total:.2f}")
        
        # Botón de WhatsApp
        mensaje = f"Hola Yalis, deseo realizar un pedido:\n\n*Producto:* {row['Nombre']}\n*Talla:* {talla_sel}\n*Cantidad:* {cantidad}\n*Total:* ${total:.2f}\n\nCódigo: {row['cod.']}"
        mensaje_encoded = urllib.parse.quote(mensaje)
        whatsapp_url = f"https://wa.me/{WHATSAPP_NUMBER}?text={mensaje_encoded}"
        
        st.markdown(f"""
            <a href="{whatsapp_url}" target="_blank" style="text-decoration: none;">
                <button style="width: 100%; background-color: #25D366; color: white; border: none; padding: 12px; cursor: pointer; font-weight: bold;">
                    RESERVAR POR WHATSAPP
                </button>
            </a>
            """, unsafe_allow_html=True)

# --- CUERPO DE LA APP ---
st.markdown("<h1 style='text-align: center;'>YALIS</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #888;'>ELEGANCIA EN CADA PASO</p>", unsafe_allow_html=True)

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(ttl="5m")
    df = df.dropna(subset=['Nombre'])

    # Grid de productos
    cols = st.columns(3)
    for index, row in df.iterrows():
        with cols[index % 3]:
            img_url = fix_drive_link(row["Imagen 1 link de la primera imagen"])
            st.image(img_url, use_container_width=True)
            st.markdown(f"### {row['Nombre']}")
            st.write(f"**${row['Precio']}**")
            
            if st.button("Comprar ahora", key=f"btn_{row['cod.']}"):
                comprar_producto(row)
            st.markdown("<br>", unsafe_allow_html=True)

except Exception as e:
    st.error("Conectando con el inventario de lujo...")
