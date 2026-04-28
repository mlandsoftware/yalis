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

# ==================== CARGA DE DATOS ====================
CSV_URL = st.secrets.get("google_sheets", {}).get("csv_url", "https://docs.google.com/spreadsheets/d/e/2PACX-1vRvD-qp4xFa_9tfSAPcQpfxRz_bOx9xjczcLAWDwM2avDd1HBpB0UEnC93bqdsOJ5a6ULVV-T7ThoI_/pub?gid=0&single=true&output=csv")
WHATSAPP_NUMBER = st.secrets.get("google_sheets", {}).get("whatsapp_number", "59398868363")

# ==================== DISEÑO PROFESIONAL (CSS CUSTOM) ====================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&family=Playfair+Display:ital,wght@0,700;1,700&display=swap');

    /* Variables de marca */
    :root {
        --primary-accent: #e94560;
        --soft-bg: #f9f9fb;
        --card-shadow: 0 10px 25px rgba(0,0,0,0.05);
    }

    .stApp { background-color: var(--soft-bg); }
    
    /* Ocultar basura visual de Streamlit */
    #MainMenu, footer, header {visibility: hidden;}

    /* Títulos Elegantes */
    .brand-title {
        font-family: 'Playfair Display', serif;
        font-size: 4rem;
        font-weight: 700;
        text-align: center;
        letter-spacing: -2px;
        margin-bottom: 0px;
    }
    .brand-subtitle {
        font-family: 'Plus Jakarta Sans', sans-serif;
        text-align: center;
        color: #666;
        font-size: 1rem;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 3rem;
    }

    /* Tarjetas de Producto (Cards) */
    div[data-testid="stVerticalBlock"] > div[style*="border: 1px solid"] {
        background-color: white !important;
        border: none !important;
        border-radius: 20px !important;
        box-shadow: var(--card-shadow) !important;
        padding: 1.5rem !important;
        transition: transform 0.3s ease;
    }
    
    div[data-testid="stVerticalBlock"] > div[style*="border: 1px solid"]:hover {
        transform: translateY(-5px);
    }

    /* Botón Negro Minimalista */
    div.stButton > button {
        background-color: #000 !important;
        color: #fff !important;
        border-radius: 50px !important;
        font-weight: 600 !important;
        letter-spacing: 0.5px !important;
        border: none !important;
        padding: 0.6rem 2rem !important;
        width: 100% !important;
        text-transform: uppercase;
        font-size: 0.8rem !important;
    }

    div.stButton > button:hover {
        background-color: var(--primary-accent) !important;
        box-shadow: 0 8px 15px rgba(233, 69, 96, 0.2) !important;
    }

    /* Precios y Etiquetas */
    .product-cat {
        color: var(--primary-accent);
        font-size: 0.75rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .product-price {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1a1a1a;
    }

    /* Selectores de Talla */
    .stSelectbox div[data-baseweb="select"] {
        border-radius: 12px !important;
        border: 1px solid #eee !important;
    }
</style>
""", unsafe_allow_html=True)

# ==================== LÓGICA DE DATOS ====================

def get_image_url(url):
    """Mejora la compatibilidad de imágenes de Drive"""
    if 'drive.google.com' in url:
        # Extrae el ID del archivo
        file_id = ""
        if 'id=' in url: file_id = url.split('id=')[-1]
        elif '/d/' in url: file_id = url.split('/d/')[1].split('/')[0]
        return f"https://drive.google.com/uc?export=view&id={file_id}"
    return url

@st.cache_data(ttl=300)
def load_data():
    try:
        df = pd.read_csv(CSV_URL)
        prods = []
        for idx, row in df.iterrows():
            # Limpiamos precios que puedan traer símbolos extraños
            raw_price = str(row.get('Precio', 0)).replace('$', '').replace(',', '.')
            try: price = float(raw_price)
            except: price = 0.0
            
            # Buscamos la primera imagen válida
            img = ""
            for col in df.columns:
                if 'imagen' in col.lower():
                    val = str(row.get(col, ''))
                    if val != 'nan' and len(val) > 10:
                        img = get_image_url(val)
                        break

            prods.append({
                'id': f"prod_{idx}",
                'name': str(row.get('Nombre', 'Calzado Premium')),
                'price': price,
                'category': str(row.get('Coleccion', 'Nueva Colección')),
                'code': str(row.get('cod.', '')),
                'image': img,
                'sizes': [t.strip() for t in str(row.get('Tallas', '35,36,37')).split(',') if t.strip()]
            })
        return prods
    except: return []

if 'cart' not in st.session_state: st.session_state.cart = []

# ==================== INTERFAZ PRINCIPAL ====================

# Encabezado Hero
st.markdown('<h1 class="brand-title">YALIS <span style="color:#e94560">CALZADO</span></h1>', unsafe_allow_html=True)
st.markdown('<p class="brand-subtitle">The Art of Walking | Ecuador 2026</p>', unsafe_allow_html=True)

all_prods = load_data()

# Filtros integrados en el diseño
f_col1, f_col2, f_col3 = st.columns([2, 2, 1])
with f_col1:
    search = st.text_input("🔍 ¿Qué buscas hoy?", placeholder="Ej: Sandalias Plateadas...")
with f_col2:
    cats = ["Todas"] + sorted(list(set(p['category'] for p in all_prods)))
    cat_sel = st.selectbox("Colección", cats)

# Filtrado lógico
filtered = [p for p in all_prods if (cat_sel == "Todas" or p['category'] == cat_sel) and (search.lower() in p['name'].lower())]

st.markdown("<br>", unsafe_allow_html=True)

# Grid de productos
if not filtered:
    st.warning("No encontramos ese estilo por ahora. ¡Intenta con otra búsqueda!")
else:
    cols = st.columns(3) # 3 productos por fila para que se vean grandes y lujosos
    for i, p in enumerate(filtered):
        with cols[i % 3]:
            with st.container(border=True):
                if p['image']:
                    st.image(p['image'], use_container_width=True)
                else:
                    st.image("https://via.placeholder.com/500x600?text=Yalis+Calzado", use_container_width=True)
                
                st.markdown(f'<p class="product-cat">{p['category']}</p>', unsafe_allow_html=True)
                st.markdown(f"### {p['name']}")
                st.markdown(f'<p class="product-price">${p['price']:.2f}</p>', unsafe_allow_html=True)
                
                talla = st.selectbox("Selecciona tu talla", p['sizes'], key=f"sz_{p['id']}")
                
                if st.button("Añadir al Carrito", key=f"btn_{p['id']}"):
                    st.session_state.cart.append({'name': p['name'], 'price': p['price'], 'size': talla})
                    st.toast(f"✨ {p['name']} listo en tu carrito")

# Carrito en Sidebar (Diseño Limpio)
with st.sidebar:
    st.markdown("## 🛒 Mi Selección")
    if not st.session_state.cart:
        st.info("Tu carrito espera por un par perfecto.")
    else:
        total = 0
        for i, item in enumerate(st.session_state.cart):
            st.markdown(f"**{item['name']}** (Talla {item['size']})")
            st.write(f"${item['price']:.2f}")
            total += item['price']
        
        st.divider()
        st.markdown(f"### Total: ${total:.2f}")
        
        msg = f"Hola Yalis! Quiero comprar:\n" + "\n".join([f"- {i['name']} ({i['size']})" for i in st.session_state.cart])
        wa_link = f"https://wa.me/{WHATSAPP_NUMBER}?text={quote(msg)}"
        
        st.link_button("💎 FINALIZAR COMPRA", wa_link)
        if st.button("Vaciar Carrito"):
            st.session_state.cart = []
            st.rerun()

st.markdown("<br><center><p style='color:#bbb; font-size:0.7rem;'>PRIVACY POLICY | TERMS OF SERVICE | © 2026 YALIS</p></center>", unsafe_allow_html=True)
