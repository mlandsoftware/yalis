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
    """Convierte URLs de Google Drive a formato directo."""
    if pd.isna(url) or url == "" or str(url).strip() == "":
        return None
    
    url_str = str(url).strip()
    patterns = [
        r'/file/d/([a-zA-Z0-9_-]+)',
        r'[?&]id=([a-zA-Z0-9_-]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url_str)
        if match:
            file_id = match.group(1)
            return f"https://drive.google.com/uc?export=view&id={file_id}"
    
    return url_str

def formatear_precio(precio):
    try:
        return float(precio)
    except (ValueError, TypeError):
        return 0.0

def obtener_tallas(tallas_str):
    if pd.isna(tallas_str) or str(tallas_str).strip() == "":
        return []
    return [t.strip() for t in str(tallas_str).split(',') if t.strip()]

# ---------------------------
# CONEXIÓN A GOOGLE SHEETS
# ---------------------------
@st.cache_data(ttl=300)
def cargar_datos():
    try:
        scope = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        
        creds_dict = st.secrets["gcp_service_account"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        
        spreadsheet = client.open_by_url(SHEET_URL)
        sheet = spreadsheet.worksheet("web")
        data = sheet.get_all_records()
        
        if not data:
            return pd.DataFrame()
        
        df = pd.DataFrame(data)
        
        # DEBUG: Mostrar nombres reales de columnas (solo para desarrollo)
        # st.write("Columnas detectadas:", list(df.columns))
        
        # Normalizar nombres de columnas (quitar espacios extra, minúsculas)
        df.columns = df.columns.str.strip()
        
        # Mapear columnas por nombre parcial (más robusto)
        column_mapping = {}
        for col in df.columns:
            col_lower = col.lower()
            if 'cod' in col_lower:
                column_mapping['cod'] = col
            elif 'coleccion' in col_lower:
                column_mapping['coleccion'] = col
            elif 'nombre' in col_lower:
                column_mapping['nombre'] = col
            elif 'precio' in col_lower:
                column_mapping['precio'] = col
            elif 'tallas' in col_lower:
                column_mapping['tallas'] = col
            elif 'promocion' in col_lower:
                column_mapping['promocion'] = col
            elif 'imagen 1' in col_lower or 'primera' in col_lower:
                column_mapping['imagen1'] = col
            elif 'imagen 2' in col_lower or 'segunda' in col_lower:
                column_mapping['imagen2'] = col
            elif 'imagen 3' in col_lower or 'tercera' in col_lower:
                column_mapping['imagen3'] = col
        
        # Verificar que tenemos las columnas mínimas necesarias
        required = ['cod', 'nombre', 'precio']
        missing = [r for r in required if r not in column_mapping]
        if missing:
            st.error(f"❌ Columnas faltantes en la hoja: {missing}")
            st.write("Columnas detectadas:", list(df.columns))
            return pd.DataFrame()
        
        # Crear DataFrame limpio con nombres estandarizados
        df_clean = pd.DataFrame()
        df_clean['Cod'] = df[column_mapping['cod']]
        df_clean['Coleccion'] = df[column_mapping.get('coleccion', df.columns[1])] if 'coleccion' in column_mapping else 'General'
        df_clean['Nombre'] = df[column_mapping['nombre']]
        df_clean['Precio'] = df[column_mapping['precio']].apply(formatear_precio)
        df_clean['Tallas'] = df[column_mapping.get('tallas', df.columns[4])].apply(obtener_tallas) if 'tallas' in column_mapping else [[] for _ in range(len(df))]
        df_clean['Promocion'] = df[column_mapping.get('promocion', df.columns[5])] if 'promocion' in column_mapping else ''
        df_clean['Imagen1'] = df[column_mapping['imagen1']].apply(convertir_url_drive) if 'imagen1' in column_mapping else None
        df_clean['Imagen2'] = df[column_mapping['imagen2']].apply(convertir_url_drive) if 'imagen2' in column_mapping else None
        df_clean['Imagen3'] = df[column_mapping['imagen3']].apply(convertir_url_drive) if 'imagen3' in column_mapping else None
        
        return df_clean
        
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        return pd.DataFrame()

# ---------------------------
# ESTADO DE SESIÓN
# ---------------------------
if "cart" not in st.session_state:
    st.session_state.cart = []

# ---------------------------
# CARGAR DATOS
# ---------------------------
df = cargar_datos()

# ---------------------------
# UI PRINCIPAL
# ---------------------------
st.title("👠 Yalis - Tienda de Calzado para Dama")
st.markdown("*Elegancia y estilo en cada paso*")
st.markdown("---")

if df.empty:
    st.warning("⚠️ No se pudieron cargar los productos.")
    st.stop()

# Filtros
colecciones = ["Todas"] + sorted([c for c in df['Coleccion'].unique() if pd.notna(c) and str(c).strip()])
col1, col2 = st.columns([1, 3])
with col1:
    filtro_coleccion = st.selectbox("📂 Filtrar por colección:", colecciones)

df_filtrado = df[df['Coleccion'] == filtro_coleccion].reset_index(drop=True) if filtro_coleccion != "Todas" else df.copy()
st.markdown(f"**Mostrando {len(df_filtrado)} productos**")
st.markdown("---")

# Grid de productos
cols = st.columns(3)

for i, row in df_filtrado.iterrows():
    with cols[i % 3]:
        with st.container():
            st.caption(f"🏷️ {row['Cod']} | 📂 {row['Coleccion']}")
            st.subheader(row['Nombre'])
            
            # Imágenes
            imagenes = []
            if pd.notna(row['Imagen1']) and row['Imagen1']:
                imagenes.append(row['Imagen1'])
            if pd.notna(row['Imagen2']) and row['Imagen2']:
                imagenes.append(row['Imagen2'])
            if pd.notna(row['Imagen3']) and row['Imagen3']:
                imagenes.append(row['Imagen3'])
            
            if imagenes:
                st.image(imagenes[0], use_container_width=True)
                if len(imagenes) > 1:
                    mini_cols = st.columns(len(imagenes))
                    for idx, img in enumerate(imagenes):
                        with mini_cols[idx]:
                            st.image(img, use_container_width=True)
            else:
                st.info("🖼️ Sin imagen")
            
            # Precio
            col_p1, col_p2 = st.columns(2)
            with col_p1:
                st.markdown(f"### 💰 ${row['Precio']:.2f}")
            with col_p2:
                promo = str(row['Promocion']).strip()
                if promo and promo.lower() not in ['nan', 'none', '']:
                    st.markdown(f"🏷️ **{promo}**")
            
            # Tallas
            tallas = row['Tallas'] if isinstance(row['Tallas'], list) else []
            talla_key = f"talla_{row['Cod']}_{i}"
            
            if tallas:
                talla_sel = st.selectbox("👟 Talla:", options=tallas, key=talla_key)
            else:
                talla_sel = "Única"
                st.write("📏 Talla única")
            
            # Botón agregar
            btn_key = f"btn_{row['Cod']}_{i}"
            if st.button(f"🛒 Agregar", key=btn_key
