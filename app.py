import json
import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ✅ Configuración de la página
st.set_page_config(page_title="Portal - Departamento de Traslados", layout="wide")

# 🔧 Ocultar la barra superior y el menú de Streamlit
hide_streamlit_style = """
    <style>
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# 🔐 Autenticación con Google Sheets desde Streamlit Secrets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
service_account_info = st.secrets["gcp_service_account"]
credentials = ServiceAccountCredentials.from_json_keyfile_dict(service_account_info, scope)

# 🔹 Autenticación con Google Sheets
client = gspread.authorize(credentials)

# 📂 Cargar datos desde Google Sheets
SHEET_ID = "1kBLQAdhYbnP8HTUgpr_rmmGEaOdyMU2tI97ogegrGxY"
SHEET_NAME = "Traslados"
sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)

def cargar_enlaces():
    data = sheet.get_all_records()
    return pd.DataFrame(data)

enlaces_df = cargar_enlaces()

# 🔐 Modo Administrador con usuario y contraseña en la barra lateral dentro de un panel minimizable
modo_admin = False
with st.sidebar:
    with st.expander("🔧 Administrador", expanded=False):
        if st.checkbox("Activar Modo Administrador"):
            usuario = st.text_input("👤 Usuario")
            password = st.text_input("🔑 Contraseña", type="password")
            if usuario == "ivan.amador" and password == "EMVac1997-":
                modo_admin = True
                st.success("🔓 Acceso concedido al modo administrador")
                
                # 🛠️ Panel de carga de enlaces justo debajo de la autenticación
                st.header("📥 Agregar Enlace")
                with st.form("Agregar Enlace"):
                    nombre = st.text_input("Nombre del Enlace")
                    url = st.text_input("URL")
                    categoria = st.selectbox("Categoría", ["Sistemas EMV", "Otros Enlaces"])
                    enviar = st.form_submit_button("Guardar Enlace")
                    
                    if enviar:
                        nuevo_enlace = [nombre, url, categoria]
                        sheet.append_row(nuevo_enlace)
                        st.success("✅ Enlace agregado exitosamente.")
                        st.rerun()

# 🏗️ Dividir la pantalla en 2 columnas con el 75% para enlaces y 25% para la calculadora
col_enlaces, col_calculadora = st.columns([5, 1])

# 🔗 Sección de accesos rápidos organizados en 5 columnas alineadas (Columna central)
with col_enlaces:
    # 📌 Agregar el logo en la parte superior con tamaño reducido
    st.image("https://github.com/ivan-emv/acceso-agentes/blob/main/a1.png?raw=true", width=500)
    
    st.header("🔗 Accesos Rápidos")
    categorias_validas = ["Sistemas EMV", "Otros Enlaces"]
    categorias = {cat: [] for cat in categorias_validas}
    
    for _, row in enlaces_df.iterrows():
        categoria = str(row.get("Categoría", "Otros enlaces")).strip()
        nombre = str(row.get("Nombre del Enlace", "")).strip()
        url = str(row.get("URL", "")).strip()
        
        if categoria in categorias and nombre and url:
            categorias[categoria].append((nombre, url))
    
    # Asegurar la alineación de los botones agregando placeholders vacíos
    max_items = max(len(cat) for cat in categorias.values())
    
    col1, col2 = st.columns(2)
    columnas = [col1, col2]
    
    for i, categoria in enumerate(categorias_validas):
        with columnas[i]:
            st.markdown(f"<h3 style='text-align: center;'>{categoria}</h3>", unsafe_allow_html=True)
            enlaces = categorias[categoria]
            for nombre, url in enlaces:
                if nombre and url:
                    st.link_button(nombre, url, use_container_width=True)
            # Rellenar con espacios en blanco para mantener la alineación
            for _ in range(max_items - len(enlaces)):
                st.markdown("&nbsp;")

# 💰 Calculadora de Reembolsos y botones adicionales (Columna derecha, ahora más estrecha)
with col_calculadora:
    st.header("Accesos Reservas y TR")
    
    st.markdown("---")
        
    localizador = st.text_input("Inserte Localizador")
    if localizador:
        st.link_button("Ver Reserva", f"https://www.europamundo-online.com/reservas/buscarreserva2.asp?coreserva={localizador}", use_container_width=True)
    
    tr = st.text_input("Inserte TR")
    if tr:
        st.link_button("Ver Traslado", f"https://www.europamundo-online.com/Individuales/ExcursionDetalle.ASP?CORESERVA={tr}", use_container_width=True)
