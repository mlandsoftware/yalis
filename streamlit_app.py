import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from urllib.parse import quote
import re

# ---------------------------
# CONFIGURACIÓN
# ---------------------------
SHEET_URL = "https://docs.google.com/spreadsheets/d/1HaH2d9O7zQUSDtKE7GoA2EZcQetINyOr48YpA_QRcpw/edit?usp=sharing"
WHATSAPP_NUMBER = "593978981018"

st.set_page_config(
    page_title="Yalis - Tienda de Calzado",
    page_icon="👠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------
# FUNCIONES AUXILIARES
# ---------------------------

def convertir_url_drive(url):
    """
    Convierte URLs de Google Drive a formato directo para mostrar imágenes.
    """
    if pd.isna(url) or url == "" or str(url).strip() == "":
        return None
    
    url_str = str(url).strip()
    
    # Extraer FILE_ID de diferentes formatos de URL de Drive
    patterns = [
        r'/file/d/([a-zA-Z0-9_-]+)',  # formato: /file/d/ID/view
        r'[?&]id=([a-zA-Z0-9_-]+)',    # formato: open?id=ID
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url_str)
        if match:
            file_id = match.group(1)
            return f"https://drive.google.com/uc?export=view&id={file_id}"
    
    return url_str

def formatear_precio(precio):
    """Convierte el precio a número float."""
    try:
        return float(precio)
    except (ValueError, TypeError):
        return 0.0

def obtener_tallas(tallas_str):
    """Convierte string de tallas en lista."""
    if pd.isna(tallas_str) or str(tallas_str).strip() == "":
        return []
    return [t.strip() for t in str(tallas_str).split(',') if t.strip()]

# ---------------------------
# CONEXIÓN A GOOGLE SHEETS (con cache)
# ---------------------------
@st.cache_data(ttl=300)
def cargar_datos():
    """Carga los datos de la pestaña 'web' del Google Sheet."""
    try:
        scope = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        
        # Obtener credenciales de Streamlit Secrets
        creds_dict = st.secrets["gcp_service_account"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        
        # Abrir la hoja por URL y seleccionar pestaña "web"
        spreadsheet = client.open_by_url(SHEET_URL)
        sheet = spreadsheet.worksheet("web")
        data = sheet.get_all_records()
        
        if not data:
            return pd.DataFrame()
        
        df = pd.DataFrame(data)
        
        # Limpiar y preparar datos
        df['Precio'] = df['Precio'].apply(formatear_precio)
        df['Imagen 1'] = df['Imagen 1 link de la primera imagen'].apply(convertir_url_drive)
        df['Imagen 2'] = df['Imagen 2 link de la segunda imagen'].apply(convertir_url_drive)
        df['Imagen 3'] = df['Imagen 3 link de la tercera imagen'].apply(convertir_url_drive)
        df['Tallas_Lista'] = df['Tallas'].apply(obtener_tallas)
        
        return df
        
    except Exception as e:
        st.error(f"❌ Error al conectar con Google Sheets: {str(e)}")
        st.info("💡 Verifica que: 1) La hoja esté compartida con la cuenta de servicio, 2) Exista la pestaña 'web', 3) Las credenciales en Secrets sean correctas.")
        return pd.DataFrame()

# ---------------------------
# INICIALIZAR ESTADO DE SESIÓN
# ---------------------------
if "cart" not in st.session_state:
    st.session_state.cart = []

# ---------------------------
# CARGAR DATOS
# ---------------------------
df = cargar_datos()

# ---------------------------
# HEADER
# ---------------------------
st.title("👠 Yalis - Tienda de Calzado para Dama")
st.markdown("*Elegancia y estilo en cada paso*")
st.markdown("---")

if df.empty:
    st.warning("⚠️ No se pudieron cargar los productos. Por favor, verifica la conexión con Google Sheets.")
    st.stop()

# ---------------------------
# FILTROS (opcional)
# ---------------------------
colecciones = ["Todas"] + sorted(df['Coleccion'].dropna().unique().tolist())
col1, col2 = st.columns([1, 3])
with col1:
    filtro_coleccion = st.selectbox("📂 Filtrar por colección:", colecciones)

if filtro_coleccion != "Todas":
    df_filtrado = df[df['Coleccion'] == filtro_coleccion].reset_index(drop=True)
else:
    df_filtrado = df.copy()

st.markdown(f"**Mostrando {len(df_filtrado)} productos**")
st.markdown("---")

# ---------------------------
# MOSTRAR PRODUCTOS EN GRID
# ---------------------------
cols = st.columns(3)

for i, row in df_filtrado.iterrows():
    with cols[i % 3]:
        with st.container():
            # Código y colección
            st.caption(f"🏷️ {row['Cod']} | 📂 {row['Coleccion']}")
            st.subheader(row['Nombre'])
            
            # Galería de imágenes
            imagenes = []
            if pd.notna(row['Imagen 1']) and row['Imagen 1']:
                imagenes.append(row['Imagen 1'])
            if pd.notna(row['Imagen 2']) and row['Imagen 2']:
                imagenes.append(row['Imagen 2'])
            if pd.notna(row['Imagen 3']) and row['Imagen 3']:
                imagenes.append(row['Imagen 3'])
            
            if imagenes:
                # Mostrar primera imagen
                st.image(imagenes[0], use_container_width=True)
                
                # Miniaturas si hay más imágenes
                if len(imagenes) > 1:
                    mini_cols = st.columns(len(imagenes))
                    for idx, img_url in enumerate(imagenes):
                        with mini_cols[idx]:
                            st.image(img_url, use_container_width=True)
            else:
                st.info("🖼️ Imagen no disponible")
            
            # Precio y promoción
            col_p1, col_p2 = st.columns(2)
            with col_p1:
                st.markdown(f"### 💰 ${row['Precio']:.2f}")
            with col_p2:
                if pd.notna(row['Promocion']) and str(row['Promocion']).strip():
                    st.markdown(f"🏷️ **{row['Promocion']}**")
            
            # Selector de talla
            tallas = row['Tallas_Lista']
            talla_key = f"talla_{row['Cod']}_{i}"
            
            if tallas:
                talla_sel = st.selectbox("👟 Talla:", options=tallas, key=talla_key)
            else:
                talla_sel = "Única"
                st.write("📏 Talla única")
            
            # Botón agregar al carrito
            btn_key = f"btn_{row['Cod']}_{i}"
            if st.button(f"🛒 Agregar", key=btn_key, use_container_width=True, type="primary"):
                producto = {
                    'codigo': row['Cod'],
                    'nombre': row['Nombre'],
                    'precio': row['Precio'],
                    'talla': talla_sel,
                    'coleccion': row['Coleccion']
                }
                st.session_state.cart.append(producto)
                st.success(f"✅ ¡Agregado!")
                st.rerun()
            
            st.markdown("---")

# ---------------------------
# SIDEBAR - CARRITO
# ---------------------------
st.sidebar.title("🛒 Tu Carrito")

if not st.session_state.cart:
    st.sidebar.info("El carrito está vacío. ¡Agrega algunos productos! 👠")
else:
    total = 0
    mensaje = "Hola Yalis! 👋%0AQuiero hacer este pedido:%0A%0A"
    
    for idx, item in enumerate(st.session_state.cart):
        st.sidebar.markdown(f"**{item['nombre']}**")
        st.sidebar.caption(f"Talla: {item['talla']} | ${item['precio']:.2f}")
        
        # Botón eliminar
        if st.sidebar.button("🗑️ Quitar", key=f"del_{idx}"):
            st.session_state.cart.pop(idx)
            st.rerun()
        
        st.sidebar.markdown("---")
        
        total += item['precio']
        mensaje += f"• {item['nombre']} (Talla {item['talla']}) - ${item['precio']:.2f}%0A"
    
    # Total
    st.sidebar.markdown(f"### 💰 Total: ${total:.2f}")
    mensaje += f"%0A💰 *Total: ${total:.2f}*%0A%0AGracias! 😊"
    
    # Botón WhatsApp
    st.sidebar.markdown("---")
    if st.sidebar.button("📱 Finalizar compra por WhatsApp", use_container_width=True, type="primary"):
        url = f"https://wa.me/{WHATSAPP_NUMBER}?text={quote(mensaje)}"
        st.sidebar.markdown(f"[👉 Hacer clic aquí para enviar por WhatsApp]({url})", unsafe_allow_html=True)
        
        # Mostrar mensaje para copiar
        with st.sidebar.expander("📋 Copiar mensaje manualmente"):
            st.code(mensaje.replace('%0A', '\n').replace('*', ''))

# ---------------------------
# FOOTER
# ---------------------------
st.markdown("---")
st.caption("© 2026 Yalis - Tienda de Calzado para Dama | Hecho con ❤️ en Ecuador")
