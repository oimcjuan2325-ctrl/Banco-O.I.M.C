import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Banco O.I.M.C. Nube", page_icon="🏛️")

# 2. ENLACE AL EXCEL (Pon aquí tu enlace de Google Sheets)
# IMPORTANTE: El enlace debe terminar en /export?format=csv
URL = "https://docs.google.com/spreadsheets/d/1tfFblkVs5AcPGQFXHIv9lHE2I8MKvZTc-yApAnEWKRc/export? format=csv"

# Función para cargar datos
def cargar_datos():
    try:
        return pd.read_csv(URL)
    except:
        return None

# Carga inicial
if 'df' not in st.session_state:
    st.session_state.df = cargar_datos()

if 'usuario_identificado' not in st.session_state:
    st.session_state.usuario_identificado = None

# 3. INTERFAZ
st.title("🏛️ O.I.M.C. Terminal (Nube)")

if st.session_state.df is None:
    st.error("❌ No se pudo conectar con el Excel. Revisa el enlace en el código.")
    st.info("Asegúrate de que el enlace termine en: /export?format=csv")
else:
    # LOGIN
    if st.session_state.usuario_identificado is None:
        with st.form("login"):
            u = st.text_input("Usuario")
            p = st.text_input("PIN", type="password")
            if st.form_submit_button("Entrar"):
                # Verificar credenciales
                user_data = st.session_state.df[st.session_state.df['Usuario'] == u]
                if not user_data.empty and str(user_data.iloc[0]['PIN']) == p:
                    st.session_state.usuario_identificado = u
                    st.rerun()
                else:
                    st.error("Usuario o PIN incorrectos")
    else:
        # PANEL DE CONTROL
        user = st.session_state.usuario_identificado
        # Sacar datos del DF
        idx = st.session_state.df[st.session_state.df['Usuario'] == user].index[0]
        saldo = st.session_state.df.at[idx, 'Saldo']
        
        st.subheader(f"Bienvenido, {user}")
        st.metric("Tu Saldo", f"{saldo} OI")
        
        if st.button("Cerrar Sesión"):
            st.session_state.usuario_identificado = None
            st.rerun()
        
        # SOLO JUAN VE LA GESTIÓN
        if user == "Juan":
            st.write("---")
            st.write("👑 Gestión de Alianza activa (Datos leídos del Excel)")
            st.dataframe(st.session_state.df) # Ver todos los saldos
