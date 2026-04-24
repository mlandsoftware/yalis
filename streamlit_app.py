import streamlit as st
import pandas as pd
import re
from urllib.parse import quote

# ==================== PAGE CONFIG ====================
st.set_page_config(
    page_title="Yalis Calzado - Tienda Online",
    page_icon="👠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==================== SECRETS & DATA ====================
CSV_URL = st.secrets.get("google_sheets", {}).get("csv_url", "https://docs.google.com/spreadsheets/d/e/2PACX-1vRvD-qp4xFa_9tfSAPcQpfxRz_bOx9xjczcLAWDwM2avDd1HBpB0UEnC93bqdsOJ5a6ULVV-T7ThoI_/pub?gid=0&single=true&output=csv")
WHATSAPP_NUMBER = st.secrets.get("google_sheets", {}).get("whatsapp_number", "59398868363")

# ==================== STYLING (CSS) ====================
st.markdown("""
<style>
    /* Importar fuente */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
    
    html, body, [class*="st-"] {
        font-family: 'Inter', sans-serif;
    }

    /* Ocultar elementos de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Botón principal estilo 'Lujo' */
    div.stButton > button:first-child {
        background: #1a1a2e !important;
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 0.5rem 1rem !important;
        transition: all 0.3s ease;
        width: 100%;
    }
    div.stButton > button:hover {
        background: #e94560 !important;
        transform: translateY(-2px);
    }

    /* Estilo de los selectores de imagen (bolitas) */
    div[data-testid="column"] button {
        background-color: transparent !important;
        border: 1px solid #ddd !important;
        color: #333 !important;
        padding: 2px !important;
        font-size: 10px !important;
        height: auto !important;
    }

    /* Cards de productos */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: white;
        border-radius: 15px !important;
        transition: box-shadow 0.3s ease;
    }
    [data-testid="stVerticalBlockBorderWrapper"]:hover {
        box-shadow: 0 10px 25px rgba(0,0,0,0.1) !important;
    }

    .price-text {
        font-size: 22px;
        font-weight: 800;
        color: #1a1a2e;
        margin: 0;
    }
</style>
""", unsafe_allow_html=True)

# ==================== DATA LOADING ====================
@st.cache_data(ttl=300)
def load_products():
    try:
        df = pd.read_csv(CSV_URL)
        products = []
        for idx, row in df.iterrows():
            # Procesar tallas
            sizes = [s.strip() for s in str(row.get('Tallas', '')).split(',') if s.strip()]
            
            # Procesar precio
            try:
                price = float(str(row.get('Precio', '0')).replace('$', '').replace(',', '.'))
            except: price = 0.0

            # Procesar imágenes de Google Drive
            images = []
            for col in df.columns:
                if 'imagen' in col.lower():
                    url = str(row.get(col, ''))
                    if 'drive.google.com' in url:
                        match = re.search(r'/d/([a-zA-Z0-9_-]+)', url)
                        if match: url = f"https://drive.google.com/uc?export=view&id={match[1]}"
                    if url and url != 'nan': images.append(url)

            products.append({
                'id': str(row.get('cod.', idx)),
                'code': str(row.get('cod.', '')),
                'collection': str(row.get('Coleccion', 'General')),
                'name': str(row.get('Nombre', 'Producto')),
                'price': price,
                'sizes': sizes,
                'images': images
            })
        return products
    except Exception as e:
        st.error(f"Error: {e}")
        return []

# ==================== HELPERS ====================
if 'cart' not in st.session_state: st.session_state.cart = []
if 'img_idx' not in st.session_state: st.session_state.img_idx = {}

def add_to_cart(product, size):
    st.session_state.cart.append({**product, 'selected_size': size})
    st.toast(f"✅ {product['name']} añadido")

# ==================== MAIN UI ====================
products = load_products()

# Hero Header
st.markdown(f"""
    <div style="text-align: center; padding: 2rem 0;">
        <h1 style='font-weight: 800; color: #1a1a2e;'>Calzado con <span style='color: #e94560;'>Estilo</span> y Elegancia</h1>
        <p style='color: #666;'>Nueva Colección 2026 - Envíos a todo el país</p>
    </div>
""", unsafe_allow_html=True)

# Filtros
col_f1, col_f2 = st.columns([1, 2])
with col_f1:
    cats = ["Todos"] + sorted(list(set(p['collection'] for p in products)))
    category = st.selectbox("Colección", cats)
with col_f2:
    search = st.text_input("Buscar por nombre o código", placeholder="Ej: Bota de Cuero")

# Filtrado lógico
filtered = [p for p in products if (category == "Todos" or p['collection'] == category) and 
            (search.lower() in p['name'].lower() or search.lower() in p['code'].lower())]

# Grid de Productos
cols_per_row = 4
rows = [filtered[i:i + cols_per_row] for i in range(0, len(filtered), cols_per_row)]

for row in rows:
    cols = st.columns(cols_per_row)
    for i, product in enumerate(row):
        with cols[i]:
            # Contenedor con borde (Card)
            with st.container(border=True):
                # Gestión de imágenes
                prod_id = product['id']
                if prod_id not in st.session_state.img_idx:
                    st.session_state.img_idx[prod_id] = 0
                
                curr_img = st.session_state.img_idx[prod_id]
                if product['images']:
                    st.image(product['images'][curr_img], use_container_width=True)
                    
                    # Mini-galería si hay más de una foto
                    if len(product['images']) > 1:
                        sub_cols = st.columns(len(product['images']))
                        for btn_idx in range(len(product['images'])):
                            label = "●" if btn_idx == curr_img else "○"
                            if sub_cols[btn_idx].button(label, key=f"btn_{prod_id}_{btn_idx}"):
                                st.session_state.img_idx[prod_id] = btn_idx
                                st.rerun()
                
                # Info de texto
                st.caption(f"{product['collection']} | {product['code']}")
                st.markdown(f"**{product['name']}**")
                st.markdown(f"<p class='price-text'>${product['price']:.2f}</p>", unsafe_allow_html=True)
                
                # Selector de talla y botón
                selected_size = st.selectbox("Talla", product['sizes'], key=f"size_{prod_id}")
                if st.button("Añadir al carrito", key=f"add_{prod_id}"):
                    add_to_cart(product, selected_size)

# ==================== SIDEBAR CARRITO ====================
with st.sidebar:
    st.title("🛒 Tu Pedido")
    if not st.session_state.cart:
        st.info("El carrito está vacío")
    else:
        total = 0
        whatsapp_msg = "Hola Yalis Calzado! Deseo ordenar:\n\n"
        
        for i, item in enumerate(st.session_state.cart):
            with st.container(border=True):
                st.write(f"**{item['name']}**")
                st.write(f"Talla: {item['selected_size']} | ${item['price']:.2f}")
                if st.button("Eliminar", key=f"del_{i}"):
                    st.session_state.cart.pop(i)
                    st.rerun()
                total += item['price']
                whatsapp_msg += f"- {item['name']} (Talla: {item['selected_size']}) - ${item['price']}\n"
        
        st.divider()
        st.subheader(f"Total: ${total:.2f}")
        
        whatsapp_msg += f"\n*Total: ${total:.2f}*"
        url = f"https://wa.me/{WHATSAPP_NUMBER}?text={quote(whatsapp_msg)}"
        st.link_button("Confirmar por WhatsApp 📱", url, use_container_width=True)
