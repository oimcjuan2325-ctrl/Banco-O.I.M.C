import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN Y CONEXIÓN
st.set_page_config(page_title="Banco Central O.I.M.C.", page_icon="🏛️")

# SUSTITUYE ESTO POR EL ENLACE DE TU EXCEL (asegúrate de que termine en /export?format=csv)
# Ejemplo: https://docs.google.com/spreadsheets/d/TU_ID/export?format=csv
SHEET_URL = "TU_ENLACE_AQUÍ_FORMATO_CSV"

def leer_datos():
    return pd.read_csv(SHEET_URL)

# 2. LÓGICA DE CARGA (Para que no se borre al refrescar)
if 'df' not in st.session_state:
    try:
        st.session_state.df = leer_datos()
    except:
        st.error("Error conectando con la base de datos de Google Sheets.")

if 'usuario_identificado' not in st.session_state:
    st.session_state.usuario_identificado = None

# --- LAS FUNCIONES DE SUELDO Y LOGIN SIGUEN IGUAL ---
def obtener_datos_sc(sc):
    if sc >= 90: return "Elite", 5
    elif sc >= 70: return "Estándar", 4
    elif sc >= 50: return "Riesgo", 2
    else: return "Sancionado", 0

# 3. LOGIN
if st.session_state.usuario_identificado is None:
    st.title("🏛️ Terminal O.I.M.C. (Nube)")
    with st.form("login"):
        u = st.text_input("Usuario:")
        p = st.text_input("PIN:", type="password")
        if st.form_submit_button("Entrar"):
            user_row = st.session_state.df[st.session_state.df['Usuario'] == u]
            if not user_row.empty and str(user_row.iloc[0]['PIN']) == p:
                st.session_state.usuario_identificado = u
                st.rerun()
            else: st.error("Acceso denegado.")

# 4. PANEL DE USUARIO Y GESTIÓN
else:
    user = st.session_state.usuario_identificado
    # Obtener fila del usuario actual
    idx = st.session_state.df[st.session_state.df['Usuario'] == user].index[0]
    saldo_actual = st.session_state.df.at[idx, 'Saldo']
    sc_actual = st.session_state.df.at[idx, 'SC']
    
    estatus, sueldo_v = obtener_datos_sc(sc_actual)

    st.title(f"👤 {user}")
    st.metric("Saldo Permanente", f"{saldo_actual} OI")
    st.metric("Social Credit", f"{sc_actual} pts")

    # NOTA: Para guardar los cambios de vuelta al Excel de forma automática 
    # se necesita una configuración de API de Google un poco más avanzada.
    
    st.info("⚠️ Los cambios realizados en esta sesión se guardan en la memoria. Para hacerlos permanentes en el Excel, el Administrador debe exportar los datos.")

    if user == "Juan":
        st.write("---")
        st.header("👑 Panel de Control Real")
        if st.button("💸 EJECUTAR CICLO SEMANAL"):
            for i, row in st.session_state.df.iterrows():
                _, pago = obtener_datos_sc(row['SC'])
                st.session_state.df.at[i, 'Saldo'] += pago
            st.success("¡Sueldos repartidos! Nota: Para guardar en el Excel permanentemente, usa la API de Google.")
            st.rerun()
