import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import urllib.parse

# Configuración de página
st.set_page_config(page_title="Yalis - Calzado de Dama", layout="wide")

# WhatsApp Config
NUMERO_WHATSAPP = "593978868363"

# Estilo de Lujo (CSS)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Lato:wght@300;400&display=swap');
    html, body, [class*="css"] { font-family: 'Lato', sans-serif; }
    h1, h2, h3 { font-family: 'Playfair Display', serif; letter-spacing: 2px; }
    .stButton>button { background-color: #000 !important; color: #fff !important; border-radius: 0px !important; width: 100%; border: none; }
    .promo-tag { color: #d4af37; font-weight: bold; font-size: 0.9em; }
    </style>
    """, unsafe_allow_html=True)

def fix_drive_link(link):
    if isinstance(link, str) and "drive.google.com" in link:
        try:
            file_id = link.split('/')[-2]
            return f"https://drive.google.com/uc?export=view&id={file_id}"
        except: return link
    return link

# Ventana Emergente (Pop-up) de Compra
@st.dialog("Detalles de tu Pedido")
def comprar_producto(producto):
    st.write(f"### {producto['Nombre']}")
    st.write(f"Precio Unitario: **${producto['Precio']}**")
    
    # Procesar tallas desde el Excel (asumiendo formato "36,37,38")
    lista_tallas = str(producto['Tallas']).split(',')
    
    col1, col2 = st.columns(2)
    with col1:
        talla_sel = st.selectbox("Selecciona tu talla:", lista_tallas)
    with col2:
        cantidad = st.number_input("Cantidad:", min_value=1, max_value=10, value=1)
    
    total = float(producto['Precio']) * cantidad
    st.write(f"**Total estimado: ${total:.2f}**")
    
    # Botón para enviar a WhatsApp
    if st.button("Confirmar y Enviar Pedido"):
        mensaje = (
            f"¡Hola Yalis! ✨\n\n"
            f"Me gustaría realizar un pedido:\n"
            f"👠 *Producto:* {producto['Nombre']}\n"
            f"🆔 *Código:* {producto['cod.']}\n"
            f"📏 *Talla:* {talla_sel}\n"
            f"🔢 *Cantidad:* {cantidad}\n"
            f"💰 *Total:* ${total:.2f}\n\n"
            f"¿Me podrían confirmar la disponibilidad?"
        )
        # Formatear URL para WhatsApp
        mensaje_encoded = urllib.parse.quote(mensaje)
        url_whatsapp = f"https://wa.me/{NUMERO_WHATSAPP}?text={mensaje_encoded}"
        
        st.markdown(f"""
            <meta http-equiv="refresh" content="0; url={url_whatsapp}">
            <a href="{url_whatsapp}" target="_blank" style="color: #25D366; text-decoration: none; font-weight: bold;">
                Si no se abre automáticamente, haz clic aquí para ir a WhatsApp
            </a>
            """, unsafe_allow_html=True)

# --- CABECERA ---
st.markdown("<h1 style='text-align: center;'>YALIS</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #888;'>COLECCIÓN EXCLUSIVA</p>", unsafe_allow_html=True)

# --- CONEXIÓN A GOOGLE SHEETS ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(ttl="5m") 
    df = df.dropna(subset=['Nombre']) 

    # --- GRID DE PRODUCTOS ---
    cols = st.columns(3)
    for index, row in df.iterrows():
        with cols[index % 3]:
            img_url = fix_drive_link(row["Imagen 1 link de la primera imagen"])
            st.image(img_url, use_container_width=True)
            
            st.markdown(f"### {row['Nombre']}")
            st.write(f"**${row['Precio']}**")
            
            # Al hacer clic, se abre el pop-up
            if st.button(f"Comprar", key=f"buy_{row['cod.']}"):
                comprar_producto(row)
            st.markdown("<br>", unsafe_allow_html=True)

except Exception as e:
    st.error("Error al cargar el inventario. Verifica la conexión con Google Sheets.")import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import urllib.parse

# Configuración de página
st.set_page_config(page_title="Yalis - Calzado de Dama", layout="wide")

# WhatsApp Config
NUMERO_WHATSAPP = "593978868363"

# Estilo de Lujo (CSS)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Lato:wght@300;400&display=swap');
    html, body, [class*="css"] { font-family: 'Lato', sans-serif; }
    h1, h2, h3 { font-family: 'Playfair Display', serif; letter-spacing: 2px; }
    .stButton>button { background-color: #000 !important; color: #fff !important; border-radius: 0px !important; width: 100%; border: none; }
    .promo-tag { color: #d4af37; font-weight: bold; font-size: 0.9em; }
    </style>
    """, unsafe_allow_html=True)

def fix_drive_link(link):
    if isinstance(link, str) and "drive.google.com" in link:
        try:
            file_id = link.split('/')[-2]
            return f"https://drive.google.com/uc?export=view&id={file_id}"
        except: return link
    return link

# Ventana Emergente (Pop-up) de Compra
@st.dialog("Detalles de tu Pedido")
def comprar_producto(producto):
    st.write(f"### {producto['Nombre']}")
    st.write(f"Precio Unitario: **${producto['Precio']}**")
    
    # Procesar tallas desde el Excel (asumiendo formato "36,37,38")
    lista_tallas = str(producto['Tallas']).split(',')
    
    col1, col2 = st.columns(2)
    with col1:
        talla_sel = st.selectbox("Selecciona tu talla:", lista_tallas)
    with col2:
        cantidad = st.number_input("Cantidad:", min_value=1, max_value=10, value=1)
    
    total = float(producto['Precio']) * cantidad
    st.write(f"**Total estimado: ${total:.2f}**")
    
    # Botón para enviar a WhatsApp
    if st.button("Confirmar y Enviar Pedido"):
        mensaje = (
            f"¡Hola Yalis! ✨\n\n"
            f"Me gustaría realizar un pedido:\n"
            f"👠 *Producto:* {producto['Nombre']}\n"
            f"🆔 *Código:* {producto['cod.']}\n"
            f"📏 *Talla:* {talla_sel}\n"
            f"🔢 *Cantidad:* {cantidad}\n"
            f"💰 *Total:* ${total:.2f}\n\n"
            f"¿Me podrían confirmar la disponibilidad?"
        )
        # Formatear URL para WhatsApp
        mensaje_encoded = urllib.parse.quote(mensaje)
        url_whatsapp = f"https://wa.me/{NUMERO_WHATSAPP}?text={mensaje_encoded}"
        
        st.markdown(f"""
            <meta http-equiv="refresh" content="0; url={url_whatsapp}">
            <a href="{url_whatsapp}" target="_blank" style="color: #25D366; text-decoration: none; font-weight: bold;">
                Si no se abre automáticamente, haz clic aquí para ir a WhatsApp
            </a>
            """, unsafe_allow_html=True)

# --- CABECERA ---
st.markdown("<h1 style='text-align: center;'>YALIS</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #888;'>COLECCIÓN EXCLUSIVA</p>", unsafe_allow_html=True)

# --- CONEXIÓN A GOOGLE SHEETS ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(ttl="5m") 
    df = df.dropna(subset=['Nombre']) 

    # --- GRID DE PRODUCTOS ---
    cols = st.columns(3)
    for index, row in df.iterrows():
        with cols[index % 3]:
            img_url = fix_drive_link(row["Imagen 1 link de la primera imagen"])
            st.image(img_url, use_container_width=True)
            
            st.markdown(f"### {row['Nombre']}")
            st.write(f"**${row['Precio']}**")
            
            # Al hacer clic, se abre el pop-up
            if st.button(f"Comprar", key=f"buy_{row['cod.']}"):
                comprar_producto(row)
            st.markdown("<br>", unsafe_allow_html=True)

except Exception as e:
    st.error("Error al cargar el inventario. Verifica la conexión con Google Sheets.")
