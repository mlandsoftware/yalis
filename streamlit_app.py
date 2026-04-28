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
    
    .stApp {
        background-color: #fcfcfc;
    }

    /* Botón principal y de Link */
    div.stButton > button, a[data-testid="stBaseButton-secondary"] {
        background: #000000 !important;
        color: #ffffff !important;
        border-radius: 6px !important;
        border: none !important;
        font-weight: 600 !important;
        height: 45px !important;
        width: 100% !important;
        transition: all 0.3s ease !important;
        display: flex;
        align-items: center;
        justify-content: center;
        text-decoration: none;
    }

    div.stButton > button:hover, a[data-testid="stBaseButton-secondary"]:hover {
        background: #e94560 !important;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(233, 69, 96, 0.3) !important;
        color: white !important;
    }

    /* Estilo para precios */
    .price-tag {
        font-size: 1.4rem;
        font-weight: 800;
        color: #1a1a1a;
        margin: 5px 0;
    }

    /* Sidebar (Carrito) */
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
            img_list = []
            for col in df.columns:
                if 'imagen' in col.lower():
                    val = str(row.get(col, ''))
                    if val != 'nan' and len(val) > 10:
                        img_list.append(get_google_drive_direct_url(val))
            
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

if 'cart' not in st.session_state:
    st.session_state.cart = []

# ==================== INTERFAZ DE USUARIO ====================

st.markdown("""
    <div style="text-align: center; padding: 2rem 0 1rem 0;">
        <h1 style="font-size: 3rem; font-weight: 800; letter-spacing: -1px; margin-bottom:0;">YALIS <span style="color:#e94560;">CALZADO</span></h1>
        <p style="color: #666; font-size: 1.1rem;">Elegancia y confort en cada paso | Colección 2026</p>
    </div>
""", unsafe_allow_html=True)

products = load_data()

# FILTROS
col_f1, col_f2 = st.columns([1, 1])
with col_f1:
    categories = ["Todas las colecciones"] + sorted(list(set(p['category'] for p in products)))
    cat_filter = st.selectbox("Filtrar por Colección", categories)
with col_f2:
    search_query = st.text_input("Buscar calzado...", placeholder="Nombre o código")

filtered_prods = [p for p in products if 
    (cat_filter == "Todas las colecciones" or p['category'] == cat_filter) and 
    (search_query.lower() in p['name'].lower() or search_query.lower() in p['code'].lower())]

st.divider()

# GRID DE PRODUCTOS (Adaptable)
if not filtered_prods:
    st.info("No se encontraron productos con estos filtros.")
else:
    # Definimos el número de columnas para el grid
    N_COLS = 4
    for i in range(0, len(filtered_prods), N_COLS):
        cols = st.columns(N_COLS)
        for j, product in enumerate(filtered_prods[i:i+N_COLS]):
            with cols[j]:
                with st.container(border=True):
                    if product['images']:
                        st.image(product['images'][0], use_container_width=True)
                    else:
                        st.image("https://via.placeholder.com/400x400?text=Sin+Imagen", use_container_width=True)
                    
                    st.markdown(f"<span style='color:#e94560; font-size:0.8rem; font-weight:600;'>{product['category']}</span>", unsafe_allow_html=True)
                    st.markdown(f"**{product['name']}**")
                    st.markdown(f"<p class='price-tag'>${product['price']:.2f}</p>", unsafe_allow_html=True)
                    
                    selected_size = st.selectbox("Talla:", product['sizes'], key=f"size_{product['id']}_{i+j}")
                    
                    if st.button("Añadir al Carrito", key=f"add_{product['id']}_{i+j}"):
                        st.session_state.cart.append({
                            'name': product['name'],
                            'price': product['price'],
                            'size': selected_size,
                            'code': product['code']
                        })
                        st.toast(f"✅ {product['name']} añadido")

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
        
        st.link_button("🚀 Enviar a WhatsApp", wa_url)
        if st.button("Vaciar Carrito"):
            st.session_state.cart = []
            st.rerun()

st.markdown("<br><br><center><p style='color:#888;'>© 2026 Yalis Calzado - Hecho con ❤️ en Ecuador</p></center>", unsafe_allow_html=True)
