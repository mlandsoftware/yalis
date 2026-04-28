import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Configuración de página
st.set_page_config(page_title="Yalis - Calzado de Dama", layout="wide")

# Estilo de Lujo (CSS)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Lato:wght@300;400&display=swap');
    html, body, [class*="css"] { font-family: 'Lato', sans-serif; }
    h1, h2, h3 { font-family: 'Playfair Display', serif; letter-spacing: 2px; }
    .stButton>button { background-color: #000; color: #fff; border-radius: 0px; width: 100%; }
    .promo-tag { color: #d4af37; font-weight: bold; font-size: 0.9em; }
    </style>
    """, unsafe_allow_html=True)

# Función para convertir links de Drive a directos
def fix_drive_link(link):
    if "drive.google.com" in link:
        file_id = link.split('/')[-2]
        return f"https://drive.google.com/uc?export=view&id={file_id}"
    return link

# Título Principal
st.markdown("<h1 style='text-align: center;'>YALIS</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #888;'>INVENTARIO EXCLUSIVO</p>", unsafe_allow_html=True)

# --- CONEXIÓN A GOOGLE SHEETS ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    # Cambia 'Sheet1' por el nombre de tu hoja si es diferente
    df = conn.read(ttl="10m") 
    
    # Limpieza básica de datos según tu captura
    df = df.dropna(subset=['Nombre']) 

    # --- FILTROS (SIDEBAR) ---
    st.sidebar.title("Filtros")
    coleccion = st.sidebar.multiselect("Colección", options=df["Coleccion"].unique())
    
    df_filtered = df
    if coleccion:
        df_filtered = df[df["Coleccion"].isin(coleccion)]

    # --- GRID DE PRODUCTOS ---
    cols = st.columns(3)
    for index, row in df_filtered.iterrows():
        with cols[index % 3]:
            img_url = fix_drive_link(row["Imagen 1 link de la primera imagen"])
            st.image(img_url, use_container_width=True)
            
            st.markdown(f"### {row['Nombre']}")
            if pd.notna(row['Promocion']):
                st.markdown(f"<span class='promo-tag'>{row['Promocion']}</span>", unsafe_allow_html=True)
            
            st.write(f"**Precio:** ${row['Precio']}")
            st.caption(f"Tallas: {row['Tallas']}")
            
            if st.button(f"Ver detalles", key=f"det_{row['cod.']}"):
                st.info(f"Has seleccionado {row['Nombre']}. Funcionalidad de carrito próximamente.")
            st.markdown("---")

except Exception as e:
    st.error("Conectando con la base de datos...")
    st.info("Asegúrate de configurar los Secrets en Streamlit Cloud con el link de tu hoja.")
