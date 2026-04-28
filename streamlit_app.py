import streamlit as st
import pandas as pd
import urllib.parse

# Configuración de la página
st.set_page_config(page_title="Tienda Yalis - Calzado de Dama", layout="wide")

# Datos de configuración
SHEET_ID = "1HaH2d9O7zQUSDtKE7GoA2EZcQetINyOr48YpA_QRcpw"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"
WHATSAPP_NUMBER = "593978981018"

def format_drive_url(url):
    """Convierte un enlace de compartir de Google Drive en un enlace directo para mostrar imágenes."""
    if 'drive.google.com' in str(url):
        file_id = url.split('/')[-2] if '/view' in url else url.split('=')[-1]
        return f'https://drive.google.com/uc?id={file_id}'
    return url

@st.cache_data
def load_data():
    try:
        # Cargar datos desde la hoja 'web' (según tu imagen)
        df = pd.read_csv(SHEET_URL)
        # Limpiar nombres de columnas por si acaso hay espacios
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"Error al cargar la base de datos: {e}")
        return None

def main():
    st.markdown("<h1 style='text-align: center; color: #1E4D2B;'>👠 Inventario Yalis</h1>", unsafe_allow_html=True)
    
    if 'cart' not in st.session_state:
        st.session_state.cart = []

    df = load_data()
    
    if df is not None:
        # --- Filtros en Barra Lateral ---
        st.sidebar.header("Filtrar por Colección")
        colecciones = ["Todas"] + df['Coleccion'].unique().tolist()
        col_selec = st.sidebar.selectbox("Seleccionar", colecciones)
        
        df_display = df if col_selec == "Todas" else df[df['Coleccion'] == col_selec]

        # --- Catálogo ---
        cols = st.columns(3)
        for index, row in df_display.iterrows():
            with cols[index % 3]:
                with st.container(border=True):
                    img_url = format_drive_url(row['Imagen 1 link de la primera imagen'])
                    st.image(img_url, use_container_width=True)
                    
                    st.subheader(row['Nombre'])
                    if pd.notna(row['Promocion']):
                        st.caption(f"✨ {row['Promocion']}")
                    
                    st.write(f"**Precio:** ${row['Precio']:.2f}")
                    
                    # Selección de talla
                    tallas_disponibles = str(row['Tallas']).split(',')
                    talla_selec = st.selectbox(f"Talla ({row['cod.']})", tallas_disponibles, key=f"talla_{index}")
                    
                    if st.button(f"Añadir al carrito", key=f"btn_{index}", use_container_width=True):
                        st.session_state.cart.append({
                            "cod": row['cod.'],
                            "nombre": row['Nombre'],
                            "precio": row['Precio'],
                            "talla": talla_selec
                        })
                        st.toast(f"✅ {row['Nombre']} añadido")

        # --- Carrito en Sidebar ---
        st.sidebar.markdown("---")
        st.sidebar.header("🛒 Mi Carrito")
        
        if not st.session_state.cart:
            st.sidebar.info("El carrito está vacío.")
        else:
            total = 0
            resumen_wa = "¡Hola Yalis! Quisiera pedir lo siguiente:\n\n"
            
            for i, item in enumerate(st.session_state.cart):
                st.sidebar.write(f"**{item['nombre']}** (Talla: {item['talla']}) - ${item['precio']}")
                total += item['precio']
                resumen_wa += f"• {item['nombre']} | Talla: {item['talla']} | Cod: {item['cod']} | ${item['precio']}\n"
            
            st.sidebar.write(f"### Total: ${total:.2f}")
            
            if st.sidebar.button("Vaciar Carrito"):
                st.session_state.cart = []
                st.rerun()

            # --- Botón de WhatsApp ---
            resumen_wa += f"\n💰 *Total a pagar: ${total:.2f}*"
            msg_encoded = urllib.parse.quote(resumen_wa)
            wa_url = f"https://wa.me/{WHATSAPP_NUMBER}?text={msg_encoded}"
            
            st.sidebar.markdown(f"""
                <a href="{wa_url}" target="_blank">
                    <button style="width:100%; background-color:#25D366; color:white; border:none; padding:12px; border-radius:8px; cursor:pointer; font-weight:bold; font-size:16px;">
                        📲 Enviar Pedido vía WhatsApp
                    </button>
                </a>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
