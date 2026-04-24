import streamlit as st
import pandas as pd
import urllib.request
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
# En Streamlit Cloud, ve a Settings → Secrets y agrega:
# [google_sheets]
# csv_url = "https://docs.google.com/spreadsheets/d/e/2PACX-.../pub?gid=0&single=true&output=csv"
# whatsapp_number = "59398868363"

try:
    CSV_URL = st.secrets["google_sheets"]["csv_url"]
    WHATSAPP_NUMBER = st.secrets["google_sheets"]["whatsapp_number"]
except Exception:
    # Fallback para desarrollo local
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

    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}

    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
    }
    ::-webkit-scrollbar-thumb {
        background: #e94560;
        border-radius: 4px;
    }

    /* Product card */
    .product-card {
        background: white;
        border-radius: 20px;
        overflow: hidden;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
        border: 1px solid #f0f0f0;
        height: 100%;
    }
    .product-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 12px 40px rgba(0,0,0,0.15);
    }

    /* Image slider */
    .image-container {
        position: relative;
        aspect-ratio: 4/3;
        overflow: hidden;
        background: #f8f8f8;
    }
    .image-container img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        transition: transform 0.5s ease;
    }
    .product-card:hover .image-container img {
        transform: scale(1.05);
    }

    /* Badges */
    .collection-badge {
        display: inline-block;
        background: rgba(233, 69, 96, 0.1);
        color: #e94560;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .promo-badge {
        position: absolute;
        top: 12px;
        left: 12px;
        background: linear-gradient(135deg, #e94560, #ff6b6b);
        color: white;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 700;
        z-index: 10;
        box-shadow: 0 4px 12px rgba(233, 69, 96, 0.3);
    }
    .image-counter {
        position: absolute;
        top: 12px;
        right: 12px;
        background: rgba(0,0,0,0.6);
        color: white;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 600;
        z-index: 10;
        backdrop-filter: blur(4px);
    }

    /* Price */
    .price {
        font-size: 24px;
        font-weight: 800;
        color: #1a1a2e;
    }

    /* Buttons */
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
    }
    .stButton > button:hover {
        transform: scale(1.05) !important;
        box-shadow: 0 6px 20px rgba(233, 69, 96, 0.4) !important;
    }

    /* WhatsApp button */
    .whatsapp-btn {
        background: linear-gradient(135deg, #25d366, #128c7e) !important;
        color: white !important;
        border: none !important;
        border-radius: 16px !important;
        padding: 16px 32px !important;
        font-weight: 700 !important;
        font-size: 16px !important;
        width: 100% !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 20px rgba(37, 211, 102, 0.3) !important;
    }
    .whatsapp-btn:hover {
        transform: scale(1.02) !important;
        box-shadow: 0 6px 25px rgba(37, 211, 102, 0.4) !important;
    }

    /* Cart sidebar */
    .cart-item {
        background: #f8f8f8;
        border-radius: 16px;
        padding: 16px;
        margin-bottom: 12px;
    }

    /* Size selector */
    .size-btn {
        display: inline-block;
        padding: 8px 16px;
        border: 2px solid #e0e0e0;
        border-radius: 12px;
        margin: 4px;
        cursor: pointer;
        transition: all 0.2s ease;
        font-weight: 600;
        color: #333;
    }
    .size-btn:hover, .size-btn.selected {
        background: #e94560;
        color: white;
        border-color: #e94560;
    }

    /* Hero section */
    .hero-section {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #1a1a2e 100%);
        padding: 60px 20px;
        text-align: center;
        border-radius: 0 0 40px 40px;
        margin: -80px -80px 40px -80px;
        position: relative;
        overflow: hidden;
    }
    .hero-section::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-image: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.03'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
    }

    /* Footer */
    .footer-section {
        background: #1a1a2e;
        color: white;
        padding: 40px 20px;
        margin: 60px -80px -80px -80px;
        text-align: center;
    }

    /* Responsive */
    @media (max-width: 768px) {
        .hero-section {
            margin: -80px -20px 20px -20px;
            padding: 40px 20px;
        }
        .footer-section {
            margin: 40px -20px -80px -20px;
        }
    }
</style>
""", unsafe_allow_html=True)

# ==================== SESSION STATE ====================
if 'cart' not in st.session_state:
    st.session_state.cart = []
if 'selected_product' not in st.session_state:
    st.session_state.selected_product = None
if 'selected_size' not in st.session_state:
    st.session_state.selected_size = None
if 'current_category' not in st.session_state:
    st.session_state.current_category = 'todos'
if 'search_term' not in st.session_state:
    st.session_state.search_term = ''

# ==================== DATA LOADING ====================
@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_products():
    """Load products from Google Sheets CSV"""
    try:
        df = pd.read_csv(CSV_URL)

        products = []
        for idx, row in df.iterrows():
            # Parse sizes
            sizes_str = str(row.get('Tallas', ''))
            sizes = [s.strip() for s in sizes_str.split(',') if s.strip()]

            # Parse price
            price_str = str(row.get('Precio', '0'))
            price = float(price_str.replace(',', '.')) if price_str.replace(',', '.').replace('.', '').isdigit() else 0

            # Find image columns dynamically
            images = []
            for col in df.columns:
                if 'imagen' in col.lower() or 'image' in col.lower():
                    url = str(row.get(col, ''))
                    if url and url != 'nan':
                        # Convert Google Drive sharing URL to direct view URL
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
    """Extract unique collections from products"""
    collections = set()
    for p in products:
        if p['collection'] and p['collection'] != 'nan':
            collections.add(p['collection'])
    return sorted(list(collections))

# ==================== CART FUNCTIONS ====================
def add_to_cart(product, size):
    """Add product to cart"""
    existing = None
    for item in st.session_state.cart:
        if item['id'] == product['id'] and item['size'] == size:
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

    st.success(f"✅ ¡{product['name']} (Talla {size}) agregado al carrito!")
    st.balloons()

def remove_from_cart(index):
    """Remove item from cart"""
    st.session_state.cart.pop(index)
    st.rerun()

def update_quantity(index, delta):
    """Update item quantity"""
    st.session_state.cart[index]['quantity'] += delta
    if st.session_state.cart[index]['quantity'] <= 0:
        st.session_state.cart.pop(index)
    st.rerun()

def get_cart_total():
    """Calculate cart total"""
    return sum(item['price'] * item['quantity'] for item in st.session_state.cart)

def get_cart_count():
    """Get total items in cart"""
    return sum(item['quantity'] for item in st.session_state.cart)

def generate_whatsapp_message():
    """Generate WhatsApp order message"""
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

# ==================== UI COMPONENTS ====================
def render_product_card(product):
    """Render a single product card"""
    with st.container():
        st.markdown(f"""
        <div class="product-card">
            <div class="image-container">
                {f'<div class="promo-badge">🏷️ {product["promotion"]}</div>' if product['promotion'] and product['promotion'] != 'nan' else ''}
                {f'<div class="image-counter">📷 {product["image_count"]} fotos</div>' if product['image_count'] > 1 else ''}
                <img src="{product['images'][0] if product['images'] else 'https://via.placeholder.com/400x300?text=Sin+Imagen'}" 
                     alt="{product['name']}" 
                     onerror="this.src='https://via.placeholder.com/400x300?text=Sin+Imagen'">
            </div>
            <div style="padding: 20px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <span class="collection-badge">{product['collection']}</span>
                    <span style="font-size: 11px; color: #999; font-family: monospace;">{product['code']}</span>
                </div>
                <h3 style="font-size: 16px; font-weight: 700; color: #1a1a2e; margin: 8px 0; line-height: 1.3;">{product['name']}</h3>
                <div style="display: flex; align-items: center; gap: 4px; margin-bottom: 12px;">
                    <span style="color: #ffc107;">⭐⭐⭐⭐⭐</span>
                    <span style="font-size: 12px; color: #999;">(4.5)</span>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span class="price">${product['price']:.2f}</span>
                </div>
                <p style="font-size: 12px; color: #666; margin-top: 12px; padding-top: 12px; border-top: 1px solid #f0f0f0;">
                    📏 Tallas: <strong>{', '.join(product['sizes'])}</strong>
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Add to cart button
        if st.button("🛒 Agregar al Carrito", key=f"btn_{product['id']}"):
            st.session_state.selected_product = product
            st.session_state.selected_size = None
            st.session_state.show_size_modal = True
            st.rerun()

def render_size_selector():
    """Render size selection modal"""
    if st.session_state.get('show_size_modal') and st.session_state.selected_product:
        product = st.session_state.selected_product

        with st.modal("Selecciona tu talla"):
            st.subheader(product['name'])
            st.write(f"💰 Precio: **${product['price']:.2f}**")
            st.write("👇 Selecciona una talla:")

            cols = st.columns(min(len(product['sizes']), 6))
            selected_size = None

            for i, size in enumerate(product['sizes']):
                with cols[i % 6]:
                    if st.button(size, key=f"size_{size}_{product['id']}", 
                                type="primary" if st.session_state.selected_size == size else "secondary"):
                        st.session_state.selected_size = size
                        st.rerun()

            if st.session_state.selected_size:
                st.success(f"✅ Talla {st.session_state.selected_size} seleccionada")

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("❌ Cancelar", use_container_width=True):
                        st.session_state.show_size_modal = False
                        st.session_state.selected_product = None
                        st.session_state.selected_size = None
                        st.rerun()

                with col2:
                    if st.button("✅ Confirmar", type="primary", use_container_width=True):
                        add_to_cart(product, st.session_state.selected_size)
                        st.session_state.show_size_modal = False
                        st.session_state.selected_product = None
                        st.session_state.selected_size = None
                        st.rerun()
            else:
                if st.button("❌ Cancelar", use_container_width=True):
                    st.session_state.show_size_modal = False
                    st.session_state.selected_product = None
                    st.rerun()

def render_cart():
    """Render cart sidebar"""
    with st.sidebar:
        st.markdown("## 🛒 Tu Carrito")
        st.markdown(f"**{get_cart_count()}** artículos")
        st.divider()

        if not st.session_state.cart:
            st.info("Tu carrito está vacío 🛍️")
            st.write("Agrega productos para comenzar tu pedido")
        else:
            for i, item in enumerate(st.session_state.cart):
                with st.container():
                    cols = st.columns([1, 3, 1])
                    with cols[0]:
                        st.image(item['image'] or 'https://via.placeholder.com/80?text=Sin+Imagen', 
                                width=60, use_container_width=True)
                    with cols[1]:
                        st.write(f"**{item['name']}**")
                        st.write(f"📏 Talla: {item['size']}")
                        st.write(f"💰 ${item['price']:.2f} c/u")
                    with cols[2]:
                        st.button("🗑️", key=f"remove_{i}", on_click=remove_from_cart, args=(i,))

                    # Quantity controls
                    q_cols = st.columns([1, 2, 1, 2])
                    with q_cols[0]:
                        st.button("➖", key=f"dec_{i}", on_click=update_quantity, args=(i, -1))
                    with q_cols[1]:
                        st.write(f"**{item['quantity']}**")
                    with q_cols[2]:
                        st.button("➕", key=f"inc_{i}", on_click=update_quantity, args=(i, 1))
                    with q_cols[3]:
                        st.write(f"**${item['price'] * item['quantity']:.2f}**")

                st.divider()

            # Total
            st.markdown(f"### 💰 Total: ${get_cart_total():.2f}")

            # WhatsApp button
            whatsapp_url = f"https://wa.me/{WHATSAPP_NUMBER}?text={generate_whatsapp_message()}"
            st.markdown(f"""
                <a href="{whatsapp_url}" target="_blank">
                    <button class="whatsapp-btn">
                        📱 Enviar Pedido por WhatsApp
                    </button>
                </a>
            """, unsafe_allow_html=True)

            st.caption(f"📲 Se enviará al +{WHATSAPP_NUMBER}")

# ==================== MAIN APP ====================
def main():
    # Load products
    products = load_products()
    collections = get_collections(products)

    # Hero Section
    st.markdown("""
    <div class="hero-section">
        <div style="position: relative; z-index: 1;">
            <div style="display: inline-block; background: rgba(233, 69, 96, 0.2); backdrop-filter: blur(10px); padding: 8px 20px; border-radius: 50px; margin-bottom: 20px; border: 1px solid rgba(233, 69, 96, 0.3);">
                <span style="color: #e94560; font-weight: 600; font-size: 14px;">✨ Nueva Colección 2026</span>
            </div>
            <h1 style="font-size: 48px; font-weight: 800; margin-bottom: 16px; line-height: 1.2;">
                Calzado con <span style="color: #e94560;">Estilo</span> y <span style="color: #c9a227;">Elegancia</span>
            </h1>
            <p style="font-size: 18px; color: #b0b0b0; max-width: 600px; margin: 0 auto 30px;">
                Descubre nuestra exclusiva colección de calzado. Diseños únicos, materiales de calidad y el confort que mereces.
            </p>
            <div style="display: flex; gap: 16px; justify-content: center; flex-wrap: wrap;">
                <a href="#productos" style="background: linear-gradient(135deg, #e94560, #ff6b6b); color: white; padding: 14px 32px; border-radius: 50px; text-decoration: none; font-weight: 600; display: inline-block; box-shadow: 0 4px 20px rgba(233, 69, 96, 0.3);">Ver Productos ↓</a>
                <a href="https://wa.me/59398868363" target="_blank" style="background: rgba(255,255,255,0.1); color: white; padding: 14px 32px; border-radius: 50px; text-decoration: none; font-weight: 600; display: inline-block; border: 1px solid rgba(255,255,255,0.2); backdrop-filter: blur(10px);">💬 Contáctanos</a>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Filters
    st.markdown('<div id="productos"></div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([2, 2, 1])

    with col1:
        # Category filter
        category_options = ['Todos'] + collections
        selected_category = st.selectbox(
            "🏷️ Colección",
            category_options,
            index=0 if st.session_state.current_category == 'todos' else category_options.index(st.session_state.current_category)
        )
        st.session_state.current_category = selected_category if selected_category != 'Todos' else 'todos'

    with col2:
        # Search
        search = st.text_input("🔍 Buscar", value=st.session_state.search_term, placeholder="Nombre, código...")
        st.session_state.search_term = search.lower()

    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        st.write(f"**{len(products)}** productos")

    # Filter products
    filtered = products
    if st.session_state.current_category != 'todos':
        filtered = [p for p in filtered if p['collection'] == st.session_state.current_category]
    if st.session_state.search_term:
        filtered = [p for p in filtered if 
                   st.session_state.search_term in p['name'].lower() or
                   st.session_state.search_term in p['code'].lower() or
                   st.session_state.search_term in p['collection'].lower()]

    # Products Grid
    if not filtered:
        st.warning("🔍 No encontramos productos con esos filtros")
    else:
        # Display in grid
        cols_per_row = 4
        for i in range(0, len(filtered), cols_per_row):
            cols = st.columns(cols_per_row)
            for j, col in enumerate(cols):
                if i + j < len(filtered):
                    with col:
                        render_product_card(filtered[i + j])

    # Size selector modal
    render_size_selector()

    # Cart sidebar
    render_cart()

    # Footer
    st.markdown("""
    <div class="footer-section">
        <div style="max-width: 800px; margin: 0 auto;">
            <div style="display: flex; align-items: center; justify-content: center; gap: 12px; margin-bottom: 20px;">
                <div style="width: 40px; height: 40px; background: linear-gradient(135deg, #e94560, #ff6b6b); border-radius: 50%; display: flex; align-items: center; justify-content: center;">
                    <span style="font-size: 18px;">👠</span>
                </div>
                <div>
                    <h3 style="margin: 0; font-size: 20px;">YALIS</h3>
                    <p style="margin: 0; font-size: 12px; color: #888;">Calzado Elegante</p>
                </div>
            </div>
            <p style="color: #888; font-size: 14px; margin-bottom: 20px;">
                Ofrecemos calzado de la más alta calidad con diseños exclusivos. Tu estilo, nuestra pasión.
            </p>
            <div style="display: flex; justify-content: center; gap: 20px; margin-bottom: 20px;">
                <span style="color: #888; font-size: 14px;">📱 +593 98 868 363</span>
                <span style="color: #888; font-size: 14px;">📧 yalis.calzado@gmail.com</span>
                <span style="color: #888; font-size: 14px;">📍 Ecuador</span>
            </div>
            <p style="color: #555; font-size: 12px;">© 2026 Yalis Calzado. Todos los derechos reservados.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
