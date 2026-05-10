import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. CONFIGURACIÓN
st.set_page_config(page_title="O.I.M.C. Banco Real", page_icon="🏛️")

# 2. CONEXIÓN (Asegúrate de que el enlace sea el de "Editor")
url = "TU_URL_DE_GOOGLE_SHEETS_AQUÍ"
conn = st.connection("gsheets", type=GSheetsConnection)

# Función para leer sin caché (para ver cambios al instante)
def cargar_datos():
    return conn.read(spreadsheet=url, ttl=0)

# CARGA INICIAL
if 'df' not in st.session_state:
    st.session_state.df = cargar_datos()

# --- FUNCIÓN CRÍTICA PARA REPARAR EL ERROR ---
def guardar_en_nube(nuevo_df):
    try:
        # Intentamos actualizar la hoja
        conn.update(spreadsheet=url, data=nuevo_df)
        st.session_state.df = nuevo_df # Actualizamos la memoria local
        st.cache_data.clear() # Limpiamos basura de la memoria
        return True
    except Exception as e:
        st.error(f"Error de conexión con Google: {e}")
        return False

# --- EJEMPLO DE CÓMO CAMBIAR EL PIN ---
with st.sidebar:
    st.subheader("⚙️ Configuración")
    nuevo_pin_input = st.text_input("Nuevo PIN", type="password", max_chars=4)
    if st.button("Actualizar PIN"):
        if nuevo_pin_input:
            # Creamos una copia del mensaje para no romper nada
            temp_df = st.session_state.df.copy()
            # Cambiamos el valor en la copia
            temp_df.loc[temp_df["Usuario"] == st.session_state.logeado, "PIN"] = str(nuevo_pin_input)
            
            # Intentamos guardar
            if guardar_en_nube(temp_df):
                st.success("¡PIN guardado en Google Sheets! ✅")
                st.rerun()
