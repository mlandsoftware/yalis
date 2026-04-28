import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from urllib.parse import quote

# --------------------------
# CONFIG
# ---------------------------
SHEET_URL = "https://docs.google.com/spreadsheets/d/1HaH2d9O7zQUSDtKE7GoA2EZcQetINyOr48YpA_QRcpw"
WHATSAPP_NUMBER = "593978981018"

# ---------------------------
# CONEXIÓN GOOGLE SHEETS
# ---------------------------
scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]

creds_dict = st.secrets["gcp_service_account"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

sheet = client.open_by_url(SHEET_URL).sheet1
data = sheet.get_all_records()
df = pd.DataFrame(data)

# ---------------------------
# UI
# ---------------------------
st.title("👠 Tienda de Calzado para Dama")

if "cart" not in st.session_state:
    st.session_state.cart = []

# Mostrar productos
for i, row in df.iterrows():
    with st.container():
        st.subheader(row["nombre"])
        st.write(f"💲 {row['precio']}")
        st.image(row["imagen"], width=200)

        if st.button(f"Agregar al carrito {i}"):
            st.session_state.cart.append(row)

# ---------------------------
# CARRITO
# ---------------------------
st.sidebar.title("🛒 Carrito")

total = 0
mensaje = "Hola, quiero hacer este pedido:%0A"

for item in st.session_state.cart:
    st.sidebar.write(f"{item['nombre']} - ${item['precio']}")
    total += item["precio"]
    mensaje += f"- {item['nombre']} (${item['precio']})%0A"

st.sidebar.write(f"**Total: ${total}**")

mensaje += f"%0ATotal: ${total}"

# ---------------------------
# BOTÓN WHATSAPP
# ---------------------------
if st.sidebar.button("Finalizar compra"):
    url = f"https://wa.me/{WHATSAPP_NUMBER}?text={mensaje}"
    st.sidebar.markdown(f"[Enviar pedido por WhatsApp]({url})", unsafe_allow_html=True)
