import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. CONEXIÓN (ttl=0 para tiempo real)
conn = st.connection("gsheets", type=GSheetsConnection)

def cargar_datos():
    data = conn.read(ttl=0)
    data.columns = data.columns.str.strip() 
    return data

df = cargar_datos()

# FUNCIÓN MAESTRA PARA GUARDAR CAMBIOS
def guardar_en_excel(dataframe_actualizado):
    try:
        conn.update(data=dataframe_actualizado)
        st.cache_data.clear()
        st.success("✅ Datos sincronizados con el Excel")
        st.rerun()
    except Exception as e:
        st.error(f"Error al guardar: {e}. Revisa si el email del banco tiene permiso de EDITOR en el Excel.")

# LOGIN Y LÓGICA (Simplificada para que no falle)
if 'user' not in st.session_state:
    st.title("🏛️ Banco OIMC")
    user_list = df['Usuario'].tolist()
    user_input = st.selectbox("Usuario", user_list)
    pin_input = st.text_input("PIN", type="password")
    
    if st.button("Entrar"):
        idx = df[df['Usuario'] == user_input].index[0]
        pin_real = str(df.at[idx, 'PIN']).split('.')[0].strip()
        if pin_real == pin_input.strip():
            st.session_state.user = user_input
            st.rerun()
        else:
            st.error("PIN incorrecto")
else:
    u_id = st.session_state.user
    idx = df[df['Usuario'] == u_id].index[0]
    
    st.header(f"Hola, {u_id}")
    saldo = int(float(df.at[idx, 'Saldo']))
    st.metric("Saldo", f"{saldo} OI")

    tabs = st.tabs(["💸 Bizum", "💵 Efectivo", "🔐 PIN", "🚪 Salir"])

    with tabs[2]: # Cambio de PIN (Aquí estaba el error)
        st.subheader("Nuevo PIN")
        n_pin = st.text_input("Escribe 4 números", max_chars=4)
        if st.button("Actualizar PIN"):
            if len(n_pin) == 4 and n_pin.isdigit():
                # Actualizamos localmente
                df.at[idx, 'PIN'] = n_pin
                # Guardamos en el Excel
                guardar_en_excel(df)
            else:
                st.warning("El PIN debe ser de 4 dígitos.")
    
    with tabs[3]:
        if st.button("Cerrar Sesión"):
            del st.session_state.user
            st.rerun()

    # PANEL ADMIN
    if str(df.at[idx, 'Rol']).lower() == "admin":
        st.divider()
        st.subheader("👑 Panel Gobernador")
        # Aquí puedes añadir las funciones de impuestos y SC que ya teníamos
