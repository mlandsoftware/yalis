import streamlit as st
import pandas as pd
import re
from urllib.parse import quote

# ==================== CONFIGURACIÓN DE PÁGINA ====================
st.set_page_config(
    page_title="Yalis Calzado | Premium Store",
    page_icon="👠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==================== CARGA DE DATOS Y SECRETOS ====================
CSV_URL = st.secrets.get("google_sheets", {}).get("csv_url", "https://docs.google.com/spreadsheets/d/e/2PACX-1vRvD-qp4xFa_9tfSAPcQpfxRz_bOx9xjczcLAWDwM2avDd1HBpB0UEnC93bqdsOJ5a6ULVV-T7ThoI_/pub?gid=0&single=true&output=csv")
WHATSAPP_NUMBER = st.secrets.get("google_sheets", {}).get("whatsapp_number", "59398868363")

# ==================== ESTILOS CSS PROFESIONALES ====================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap');

    html, body, [class*="st-"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
        color: #1a1a1a;
    }

    /* Ocultar elementos innecesarios */
    #MainMenu, footer, header {visibility: hidden;}
    
    /* Fondo de la app */
    .stApp {
        background-color: #fcfcfc;
    }

    /* Botón principal (Add to Cart) */
    div.stButton > button {
        background: #000000 !important;
        color: #ffffff !important;
        border-radius: 6px !important;
        border: none !important;
        font-weight: 600 !important;
        height: 45px !important;
        width: 100% !important;
        transition: all 0.3s ease !important;
    }
    div.stButton > button:hover {
        background: #e94560 !important;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(233, 69, 96, 0.3) !important;
    }

    /* Input styling */
    .stTextInput input, .stSelectbox div {
        border-radius: 8px !important;
    }

    /* Estilo para precios */
    .price-tag {
        font-size: 1.4rem;
        font-weight: 800;
        color: #1a1a1a;
        margin: 5px 0;
    }

    /* Estilo del Sidebar (Carrito) */
    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-left: 1px solid #eee;
    }
</style>
""", unsafe_allow_html=True)

# ==================== LÓGICA DE NEGOCIO ====================

def get_google_drive_direct_url(url):
    """Convierte links de Drive en links de imagen directa."""
    if 'drive.google.com' in url:
        match = re.search(r'(?:id=|[d]/)([\w-]+)', url)
        if match:
            return f"https://drive.google.com/uc?export=view&id={match.group(1)}"
    return url

@st.cache_data(ttl=300)
def load_data():
    try:
        df = pd.read_csv(CSV_URL)
        prods = []
        for idx, row in df.iterrows():
            # Procesar imágenes
            img_list = []
            for col in df.columns:
                if 'imagen' in col.lower():
                    val = str(row.get(col, ''))
                    if val != 'nan' and len(val) > 10:
                        img_list.append(get_google_drive_direct_url(val))
            
            # Procesar tallas
            tallas = [t.strip() for t in str(row.get('Tallas', '')).split(',') if t.strip()]
            
            prods.append({
                'id': str(row.get('cod.', idx)),
                'name': str(row.get('Nombre', 'Producto')),
                'price': float(str(row.get('Precio', 0)).replace('$', '').replace(',', '.')),
                'category': str(row.get('Coleccion', 'General')),
                'code': str(row.get('cod.', '')),
                'images': img_list,
                'sizes': tallas
            })
        return prods
    except Exception as e:
        st.error(f"Error cargando datos: {e}")
        return []

# Inicializar carrito
if 'cart' not in st.session_state:
    st.session_state.cart = []

# ==================== INTERFAZ DE USUARIO ====================

# HEADER HERO
st.markdown("""
    <div style="text-align: center; padding: 3rem 0 2rem 0;">
        <h1 style="font-size: 3rem; font-weight: 800; letter-spacing: -1px;">YALIS <span style="color:#e94560;">CALZADO</span></h1>
        <p style="color: #666; font-size: 1.1rem;">Elegancia y confort en cada paso | Colección 2026</p>
    </div>
""", unsafe_allow_html=True)

products = load_data()

# FILTROS
col_f1, col_f2, col_f3 = st.columns([1, 1, 1])
with col_f1:
    categories = ["Todas las colecciones"] + sorted(list(set(p['category'] for p in products)))
    cat_filter = st.selectbox("Filtrar por Colección", categories)
with col_f2:
    search_query = st.text_input("Buscar calzado...", placeholder="Nombre o código")

# Lógica de filtrado
filtered_prods = [p for p in products if 
    (cat_filter == "Todas las colecciones" or p['category'] == cat_filter) and 
    (search_query.lower() in p['name'].lower() or search_query.lower() in p['code'].lower())]

st.divider()

# GRID DE PRODUCTOS
if not filtered_prods:
    st.info("No se encontraron productos con estos filtros.")
else:
    # Mostramos en filas de 4 columnas
    rows = [filtered_prods[i:i + 4] for i in range(0, len(filtered_prods), 4)]
    
    for row in rows:
        cols = st.columns(4)
        for i, product in enumerate(row):
            with cols[i]:
                # Usamos el contenedor nativo con borde para la "Card"
                with st.container(border=True):
                    # Imagen principal
                    if product['images']:
                        st.image(product['images'][0], use_container_width=True)
                    else:
                        st.image("https://via.placeholder.com/400x400?text=Sin+Imagen", use_container_width=True)
                    
                    # Detalles del producto
                    st.markdown(f"<span style='color:#e94560; font-size:0.8rem; font-weight:600;'>{product['category']}</span>", unsafe_allow_html=True)
                    st.markdown(f"**{product['name']}**")
                    st.markdown(f"<p class='price-tag'>${product['price']:.2f}</p>", unsafe_allow_html=True)
                    
                    # Selección de talla
                    selected_size = st.selectbox("Talla disponible:", product['sizes'], key=f"size_{product['id']}")
                    
                    if st.button("Añadir al Carrito", key=f"add_{product['id']}"):
                        st.session_state.cart.append({
                            'name': product['name'],
                            'price': product['price'],
                            'size': selected_size,
                            'code': product['code']
                        })
                        st.toast(f"✅ Añadido: {product['name']}")

# ==================== SIDEBAR (CARRITO) ====================
with st.sidebar:
    st.header("🛒 Tu Pedido")
    if not st.session_state.cart:
        st.write("El carrito está vacío.")
    else:
        total = 0
        whatsapp_text = "¡Hola Yalis Calzado! 👋 Deseo realizar este pedido:\n\n"
        
        for i, item in enumerate(st.session_state.cart):
            with st.container(border=True):
                st.write(f"**{item['name']}**")
                st.write(f"Talla: {item['size']} | ${item['price']:.2f}")
                if st.button("Quitar", key=f"remove_{i}"):
                    st.session_state.cart.pop(i)
                    st.rerun()
                total += item['price']
                whatsapp_text += f"• {item['name']} (Talla: {item['size']}) - ${item['price']:.2f}\n"
        
        st.divider()
        st.subheader(f"Total: ${total:.2f}")
        
        whatsapp_text += f"\n💰 *Total a pagar: ${total:.2f}*"
        wa_url = f"https://wa.me/{WHATSAPP_NUMBER}?text={quote(whatsapp_text)}"
        
        st.link_button("🚀 Enviar Pedido por WhatsApp", wa_url, use_container_width=True)
        if st.button("Vaciar Carrito"):
            st.session_state.cart = []
            st.rerun()

# FOOTER
st.markdown("<br><br><center><p style='color:#888;'>© 2026 Yalis Calzado - Hecho con ❤️ en Ecuador</p></center>", unsafe_allow_html=True)
