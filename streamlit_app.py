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

# ==================== SECRETS ====================
try:
    CSV_URL = st.secrets["google_sheets"]["csv_url"]
    WHATSAPP_NUMBER = st.secrets["google_sheets"]["whatsapp_number"]
except Exception:
    CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRvD-qp4xFa_9tfSAPcQpfxRz_bOx9xjczcLAWDwM2avDd1HBpB0UEnC93bqdsOJ5a6ULVV-T7ThoI_/pub?gid=0&single=true&output=csv"
    WHATSAPP_NUMBER = "59398868363"

# ==================== CUSTOM CSS ====================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');

    .stApp {
        font-family: 'Poppins', sans-serif;
        background: linear-gradient(135deg, #f5f5f5 0%, #ffffff 100%);
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}

    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: #f1f1f1; }
    ::-webkit-scrollbar-thumb { background: #e94560; border-radius: 4px; }

    .stButton > button {
        background: linear-gradient(135deg, #e94560, #ff6b6b) !important;
        color: white !important;
        border: none !important;
        border-radius: 50px !important;
        padding: 10px 24px !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(233, 69, 96, 0.3) !important;
        width: 100% !important;
    }
    .stButton > button:hover {
        transform: scale(1.05) !important;
        box-shadow: 0 6px 20px rgba(233, 69, 96, 0.4) !important;
    }

    .stButton > button[kind="secondary"] {
        background: #f0f0f0 !important;
        color: #333 !important;
        box-shadow: none !important;
    }
    .stButton > button[kind="secondary"]:hover {
        background: #e0e0e0 !important;
    }

    div[data-testid="stSidebarUserContent"] {
        padding-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# ==================== SESSION STATE ====================
if 'cart' not in st.session_state:
    st.session_state.cart = []
if 'show_size_modal' not in st.session_state:
    st.session_state.show_size_modal = False
if 'selected_product_id' not in st.session_state:
    st.session_state.selected_product_id = None
if 'selected_size' not in st.session_state:
    st.session_state.selected_size = None
if 'current_category' not in st.session_state:
    st.session_state.current_category = 'Todos'
if 'search_term' not in st.session_state:
    st.session_state.search_term = ''
if 'current_image_idx' not in st.session_state:
    st.session_state.current_image_idx = {}

# ==================== DATA LOADING ====================
@st.cache_data(ttl=300)
def load_products():
    try:
        df = pd.read_csv(CSV_URL)
        products = []
        for idx, row in df.iterrows():
            sizes_str = str(row.get('Tallas', ''))
            sizes = [s.strip() for s in sizes_str.split(',') if s.strip()]

            price_str = str(row.get('Precio', '0'))
            try:
                price = float(str(price_str).replace(',', '.'))
            except:
                price = 0.0

            images = []
            for col in df.columns:
                if 'imagen' in col.lower() or 'image' in col.lower():
                    url = str(row.get(col, ''))
                    if url and url != 'nan' and len(url) > 10:
                        match = re.search(r'/d/([a-zA-Z0-9_-]+)', url)
                        if match:
                            url = f"https://drive.google.com/uc?export=view&id={match[1]}"
                        images.append(url)

            product = {
                'id': str(row.get('cod.', f'prod-{idx}')),
                'code': str(row.get('cod.', '')),
                'collection': str(row.get('Coleccion', 'General')),
                'name': str(row.get('Nombre', 'Producto sin nombre')),
                'price': price,
                'sizes': sizes,
                'promotion': str(row.get('Promocion', '')),
                'images': images,
                'image_count': len(images)
            }
            products.append(product)
        return products
    except Exception as e:
        st.error(f"❌ Error cargando productos: {e}")
        return []

def get_collections(products):
    collections = set()
    for p in products:
        col = p['collection']
        if col and col != 'nan' and col.strip():
            collections.add(col.strip())
    return sorted(list(collections))

# ==================== CART FUNCTIONS ====================
def add_to_cart(product_id, size):
    products = load_products()
    product = next((p for p in products if p['id'] == product_id), None)
    if not product:
        return

    existing = None
    for item in st.session_state.cart:
        if item['id'] == product_id and item['size'] == size:
            existing = item
            break

    if existing:
        existing['quantity'] += 1
    else:
        st.session_state.cart.append({
            'id': product['id'],
            'code': product['code'],
            'name': product['name'],
            'price': product['price'],
            'size': size,
            'image': product['images'][0] if product['images'] else '',
            'quantity': 1
        })

    st.session_state.show_size_modal = False
    st.session_state.selected_product_id = None
    st.session_state.selected_size = None
    st.toast(f"✅ ¡{product['name']} (Talla {size}) agregado!", icon="🛒")

def remove_from_cart(index):
    st.session_state.cart.pop(index)
    st.rerun()

def update_quantity(index, delta):
    st.session_state.cart[index]['quantity'] += delta
    if st.session_state.cart[index]['quantity'] <= 0:
        st.session_state.cart.pop(index)
    st.rerun()

def get_cart_total():
    return sum(item['price'] * item['quantity'] for item in st.session_state.cart)

def get_cart_count():
    return sum(item['quantity'] for item in st.session_state.cart)

def generate_whatsapp_message():
    message = "🛒 *NUEVO PEDIDO - YALIS CALZADO*\n"
    message += "═══════════════════════\n\n"

    for i, item in enumerate(st.session_state.cart, 1):
        message += f"*{i}. {item['name']}*\n"
        message += f"   Código: {item['code']}\n"
        message += f"   Talla: {item['size']}\n"
        message += f"   Cantidad: {item['quantity']}\n"
        message += f"   Precio: ${item['price'] * item['quantity']:.2f}\n\n"

    message += "═══════════════════════\n"
    message += f"*Total: ${get_cart_total():.2f}*\n\n"
    message += "Por favor confirmar disponibilidad y forma de pago. ¡Gracias! 🙏"

    return quote(message)

# ==================== HERO SECTION ====================
def render_hero():
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 40px 20px;">
            <div style="display: inline-block; background: rgba(233, 69, 96, 0.1); padding: 8px 20px; border-radius: 50px; margin-bottom: 20px; border: 1px solid rgba(233, 69, 96, 0.2);">
                <span style="color: #e94560; font-weight: 600; font-size: 14px;">✨ Nueva Colección 2026</span>
            </div>
            <h1 style="font-size: 42px; font-weight: 800; margin-bottom: 16px; line-height: 1.2; color: #1a1a2e;">
                Calzado con <span style="color: #e94560;">Estilo</span> y <span style="color: #c9a227;">Elegancia</span>
            </h1>
            <p style="font-size: 16px; color: #666; max-width: 500px; margin: 0 auto 30px;">
                Descubre nuestra exclusiva colección de calzado. Diseños únicos, materiales de calidad y el confort que mereces.
            </p>
        </div>
        """, unsafe_allow_html=True)

        btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 1])
        with btn_col1:
            st.write("")
        with btn_col2:
            if st.button("👠 Ver Productos", use_container_width=True):
                st.markdown("<div id='productos'></div>", unsafe_allow_html=True)
        with btn_col3:
            st.write("")

# ==================== PRODUCT CARD ====================
def render_product_card(product):
    """Render product using native Streamlit components"""

    # Card container
    with st.container():
        # Image section with slider
        if product['images']:
            # Initialize image index for this product
            prod_key = f"img_idx_{product['id']}"
            if prod_key not in st.session_state.current_image_idx:
                st.session_state.current_image_idx[prod_key] = 0

            current_idx = st.session_state.current_image_idx[prod_key]
            current_img = product['images'][current_idx]

            # Display image
            st.image(current_img, use_container_width=True)

            # Image navigation (only if multiple images)
            if product['image_count'] > 1:
                nav_cols = st.columns(product['image_count'] + 2)
                with nav_cols[0]:
                    if st.button("◀", key=f"prev_{product['id']}"):
                        st.session_state.current_image_idx[prod_key] = (current_idx - 1) % product['image_count']
                        st.rerun()

                # Dot indicators
                for i in range(product['image_count']):
                    with nav_cols[i + 1]:
                        dot_color = "🔴" if i == current_idx else "⚪"
                        if st.button(dot_color, key=f"dot_{product['id']}_{i}"):
                            st.session_state.current_image_idx[prod_key] = i
                            st.rerun()

                with nav_cols[-1]:
                    if st.button("▶", key=f"next_{product['id']}"):
                        st.session_state.current_image_idx[prod_key] = (current_idx + 1) % product['image_count']
                        st.rerun()
        else:
            st.image("https://via.placeholder.com/400x300?text=Sin+Imagen", use_container_width=True)

        # Product info
        info_col1, info_col2 = st.columns([2, 1])
        with info_col1:
            st.markdown(f"<span style='background: rgba(233,69,96,0.1); color: #e94560; padding: 4px 12px; border-radius: 20px; font-size: 11px; font-weight: 600;'>{product['collection']}</span>", unsafe_allow_html=True)
        with info_col2:
            st.markdown(f"<p style='text-align: right; font-size: 11px; color: #999; font-family: monospace; margin: 0;'>{product['code']}</p>", unsafe_allow_html=True)

        st.markdown(f"<h3 style='font-size: 16px; font-weight: 700; color: #1a1a2e; margin: 8px 0; line-height: 1.3;'>{product['name']}</h3>", unsafe_allow_html=True)

        # Stars
        st.markdown("<p style='font-size: 14px; margin: 4px 0;'>⭐⭐⭐⭐⭐ <span style='color: #999; font-size: 12px;'>(4.5)</span></p>", unsafe_allow_html=True)

        # Price and add button
        price_col1, price_col2 = st.columns([1, 1])
        with price_col1:
            st.markdown(f"<p style='font-size: 24px; font-weight: 800; color: #1a1a2e; margin: 0;'>${product['price']:.2f}</p>", unsafe_allow_html=True)
        with price_col2:
            st.write("")

        # Sizes info
        st.markdown(f"<p style='font-size: 12px; color: #666; margin-top: 8px; padding-top: 8px; border-top: 1px solid #f0f0f0;'>📏 Tallas: <strong>{', '.join(product['sizes'])}</strong></p>", unsafe_allow_html=True)

        # Add to cart button
        if st.button("🛒 Agregar al Carrito", key=f"add_{product['id']}"):
            st.session_state.selected_product_id = product['id']
            st.session_state.show_size_modal = True
            st.session_state.selected_size = None
            st.rerun()

# ==================== SIZE MODAL ====================
def render_size_modal(products):
    if not st.session_state.show_size_modal or not st.session_state.selected_product_id:
        return

    product = next((p for p in products if p['id'] == st.session_state.selected_product_id), None)
    if not product:
        return

    @st.dialog("Selecciona tu talla")
    def size_dialog():
        st.subheader(product['name'])
        st.write(f"💰 Precio: **${product['price']:.2f}**")
        st.write("👇 Selecciona una talla:")

        # Size buttons in columns
        cols_per_row = 6
        for i in range(0, len(product['sizes']), cols_per_row):
            cols = st.columns(min(cols_per_row, len(product['sizes']) - i))
            for j, size in enumerate(product['sizes'][i:i+cols_per_row]):
                with cols[j]:
                    btn_type = "primary" if st.session_state.selected_size == size else "secondary"
                    if st.button(size, key=f"size_btn_{size}", type=btn_type, use_container_width=True):
                        st.session_state.selected_size = size
                        st.rerun()

        if st.session_state.selected_size:
            st.success(f"✅ Talla {st.session_state.selected_size} seleccionada")

            action_col1, action_col2 = st.columns(2)
            with action_col1:
                if st.button("❌ Cancelar", use_container_width=True):
                    st.session_state.show_size_modal = False
                    st.session_state.selected_product_id = None
                    st.session_state.selected_size = None
                    st.rerun()
            with action_col2:
                if st.button("✅ Confirmar", type="primary", use_container_width=True):
                    add_to_cart(product['id'], st.session_state.selected_size)
                    st.rerun()
        else:
            if st.button("❌ Cancelar", use_container_width=True):
                st.session_state.show_size_modal = False
                st.session_state.selected_product_id = None
                st.rerun()

    size_dialog()

# ==================== CART SIDEBAR ====================
def render_cart():
    with st.sidebar:
        st.markdown("## 🛒 Tu Carrito")
        st.write(f"**{get_cart_count()}** artículos")
        st.divider()

        if not st.session_state.cart:
            st.info("Tu carrito está vacío 🛍️")
            st.write("Agrega productos para comenzar tu pedido")
        else:
            for i, item in enumerate(st.session_state.cart):
                with st.container():
                    cart_cols = st.columns([1, 3])
                    with cart_cols[0]:
                        st.image(item['image'] or 'https://via.placeholder.com/80?text=Sin+Imagen', width=60)
                    with cart_cols[1]:
                        st.write(f"**{item['name']}**")
                        st.write(f"📏 Talla: {item['size']}")
                        st.write(f"💰 ${item['price']:.2f} c/u")

                    # Quantity controls
                    qty_cols = st.columns([1, 1, 1, 2])
                    with qty_cols[0]:
                        if st.button("➖", key=f"dec_{i}"):
                            update_quantity(i, -1)
                    with qty_cols[1]:
                        st.write(f"**{item['quantity']}**")
                    with qty_cols[2]:
                        if st.button("➕", key=f"inc_{i}"):
                            update_quantity(i, 1)
                    with qty_cols[3]:
                        st.write(f"**${item['price'] * item['quantity']:.2f}**")

                    if st.button("🗑️ Eliminar", key=f"del_{i}"):
                        remove_from_cart(i)

                st.divider()

            # Total
            st.markdown(f"### 💰 Total: ${get_cart_total():.2f}")

            # WhatsApp button
            whatsapp_url = f"https://wa.me/{WHATSAPP_NUMBER}?text={generate_whatsapp_message()}"
            st.link_button("📱 Enviar Pedido por WhatsApp", whatsapp_url, use_container_width=True)
            st.caption(f"📲 Se enviará al +{WHATSAPP_NUMBER}")

# ==================== FOOTER ====================
def render_footer():
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 30px 20px;">
        <div style="display: flex; align-items: center; justify-content: center; gap: 12px; margin-bottom: 16px;">
            <div style="width: 40px; height: 40px; background: linear-gradient(135deg, #e94560, #ff6b6b); border-radius: 50%; display: flex; align-items: center; justify-content: center;">
                <span style="font-size: 18px;">👠</span>
            </div>
            <div>
                <h3 style="margin: 0; font-size: 20px; color: #1a1a2e;">YALIS</h3>
                <p style="margin: 0; font-size: 12px; color: #888;">Calzado Elegante</p>
            </div>
        </div>
        <p style="color: #888; font-size: 14px; margin-bottom: 16px;">
            Ofrecemos calzado de la más alta calidad con diseños exclusivos. Tu estilo, nuestra pasión.
        </p>
        <p style="color: #888; font-size: 14px;">
            📱 +593 98 868 363 | 📧 yalis.calzado@gmail.com | 📍 Ecuador
        </p>
        <p style="color: #aaa; font-size: 12px; margin-top: 16px;">© 2026 Yalis Calzado. Todos los derechos reservados.</p>
    </div>
    """, unsafe_allow_html=True)

# ==================== MAIN ====================
def main():
    # Load data
    products = load_products()
    collections = get_collections(products)

    # Hero
    render_hero()

    st.markdown("<div id='productos'></div>", unsafe_allow_html=True)

    # Filters
    filter_col1, filter_col2, filter_col3 = st.columns([2, 2, 1])

    with filter_col1:
        category_options = ['Todos'] + collections
        current_idx = category_options.index(st.session_state.current_category) if st.session_state.current_category in category_options else 0
        selected = st.selectbox("🏷️ Colección", category_options, index=current_idx)
        st.session_state.current_category = selected

    with filter_col2:
        search = st.text_input("🔍 Buscar", value=st.session_state.search_term, placeholder="Nombre, código...")
        st.session_state.search_term = search.lower()

    with filter_col3:
        st.write("")
        st.write("")
        st.write(f"**{len(products)}** productos")

    # Filter products
    filtered = products
    if st.session_state.current_category != 'Todos':
        filtered = [p for p in filtered if p['collection'] == st.session_state.current_category]
    if st.session_state.search_term:
        term = st.session_state.search_term
        filtered = [p for p in filtered if 
                   term in p['name'].lower() or
                   term in p['code'].lower() or
                   term in p['collection'].lower()]

    # Products grid
    if not filtered:
        st.warning("🔍 No encontramos productos con esos filtros")
    else:
        cols_per_row = 4
        for i in range(0, len(filtered), cols_per_row):
            cols = st.columns(cols_per_row)
            for j, col in enumerate(cols):
                if i + j < len(filtered):
                    with col:
                        # Card styling with container
                        with st.container():
                            st.markdown("""
                            <div style="background: white; border-radius: 20px; overflow: hidden; 
                                        box-shadow: 0 4px 20px rgba(0,0,0,0.08); border: 1px solid #f0f0f0; 
                                        padding: 0; margin-bottom: 20px;">
                            """, unsafe_allow_html=True)
                            render_product_card(filtered[i + j])
                            st.markdown("</div>", unsafe_allow_html=True)

    # Size modal
    render_size_modal(products)

    # Cart
    render_cart()

    # Footer
    render_footer()

if __name__ == "__main__":
    main()
