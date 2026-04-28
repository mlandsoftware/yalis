import streamlit as st
import pandas as pd
import urllib.parse

# Configuración estética
st.set_page_config(page_title="Yalis | Calzado de Dama", layout="wide")

# Estilo CSS para elegancia y minimalismo
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Lato:wght@300;400&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Lato', sans-serif;
    }
    
    .main-title {
        font-family: 'Playfair Display', serif;
        color: #1a1a1a;
        text-align: center;
        font-size: 3rem;
        margin-bottom: 0.5rem;
    }
    
    .subtitle {
        text-align: center;
        color: #666;
        font-weight: 300;
        letter-spacing: 2px;
        margin-bottom: 3rem;
        text-transform: uppercase;
    }
    
    .product-card {
        border-radius: 0px;
        padding: 10px;
        transition: 0.3s;
    }
    
    .price-tag {
        font-size: 1.2rem;
        font-weight: 400;
        color: #2c2c2c;
    }
    
    div.stButton > button {
        border-radius: 0px;
        background-color: #1a1a1a;
        color: white;
        border: none;
        width: 100%;
        transition: 0.3s;
    }
    
    div.stButton > button:hover {
        background-color: #404040;
        color: white;
    }

    [data-testid="stSidebar"] {
        background-color: #f8f8f8;
    }
    </style>
    """, unsafe_allow_html=True)

# Configuración de Datos
SHEET_ID = "1HaH2d9O7zQUSDtKE7GoA2EZcQetINyOr48YpA_QRcpw"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"
WHATSAPP_NUMBER = "593978981018"

def format_drive_url(url):
    if 'drive.google.com' in str(url):
        file_id = url.split('/')[-2] if '/view' in url else url.split('=')[-1].split('&')[0]
        return f'https://drive.google.com/uc?id={file_id}'
    return url

@st.cache_data
def load_data():
    try:
        df = pd.read_csv(SHEET_URL)
        df.columns = df.columns.str.strip()
        return df
    except:
        return None

def main():
    st.markdown('<h1 class="main-title">YALIS</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Colección Exclusiva de Calzado</p>', unsafe_allow_html=True)

    if 'cart' not in st.session_state:
        st.session_state.cart = []

    df = load_data()
    
    if df is not None:
        # Filtros elegantes en la parte superior
        colecciones = ["Todas las Colecciones"] + sorted(df['Coleccion'].unique().tolist())
        col_selec = st.selectbox("", colecciones, label_visibility="collapsed")
        
        df_display = df if col_selec == "Todas las Colecciones" else df[df['Coleccion'] == col_selec]

        st.markdown("<br>", unsafe_allow_html=True)

        # Grill de Productos
        cols = st.columns(3)
        for index, row in df_display.iterrows():
            with cols[index % 3]:
                img_url = format_drive_url(row['Imagen 1 link de la primera imagen'])
                st.image(img_url, use_container_width=True)
                
                st.markdown(f"**{row['Nombre']}**")
                st.markdown(f"<p class='price-tag'>${row['Precio']:.2f}</p>", unsafe_allow_html=True)
                
                if st.button("AGREGAR AL CARRITO", key=f"add_{index}"):
                    # Guardamos el producto y sus tallas disponibles
                    st.session_state.cart.append({
                        "id": index,
                        "cod": row['cod.'],
                        "nombre": row['Nombre'],
                        "precio": row['Precio'],
                        "tallas_posibles": str(row['Tallas']).split(','),
                        "talla_seleccionada": str(row['Tallas']).split(',')[0].strip() # Default
                    })
                    st.toast("Añadido a tu selección")

        # --- SECCIÓN CARRITO (Sidebar) ---
        with st.sidebar:
            st.markdown("### MI COMPRA")
            st.markdown("---")
            
            if not st.session_state.cart:
                st.write("No hay artículos seleccionados.")
            else:
                total = 0
                resumen_wa = "¡Hola! Quisiera realizar un pedido de YALIS:\n\n"
                
                # Lista de productos en el carrito con selector de talla
                for i, item in enumerate(st.session_state.cart):
                    with st.container():
                        st.write(f"**{item['nombre']}**")
                        # Aquí el usuario elige la talla antes de confirmar
                        nueva_talla = st.selectbox(
                            f"Talla para {item['cod']}", 
                            item['tallas_posibles'], 
                            key=f"cart_talla_{i}",
                            label_visibility="collapsed"
                        )
                        st.session_state.cart[i]['talla_seleccionada'] = nueva_talla
                        
                        st.write(f"${item['precio']:.2f}")
                        total += item['precio']
                        st.markdown("---")

                st.write(f"#### TOTAL: ${total:.2f}")
                
                if st.button("LIMPIAR CARRITO"):
                    st.session_state.cart = []
                    st.rerun()

                # Preparar mensaje de WhatsApp
                for item in st.session_state.cart:
                    resumen_wa += f"• {item['nombre']} | Talla: {item['talla_seleccionada']} | Cod: {item['cod']} | ${item['precio']}\n"
                
                resumen_wa += f"\n*Total: ${total:.2f}*"
                msg_encoded = urllib.parse.quote(resumen_wa)
                wa_url = f"https://wa.me/{WHATSAPP_NUMBER}?text={msg_encoded}"
                
                st.markdown(f"""
                    <a href="{wa_url}" target="_blank" style="text-decoration: none;">
                        <div style="background-color: #1a1a1a; color: white; text-align: center; padding: 15px; font-weight: bold; letter-spacing: 1px;">
                            CONFIRMAR POR WHATSAPP
                        </div>
                    </a>
                """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
