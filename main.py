import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. CONEXIÓN Y CONFIGURACIÓN
st.set_page_config(page_title="O.I.M.C. Banco Central", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(ttl=0)

# Lógica oficial de sueldos según Social Credit (SC)
def calc_sueldo(sc):
    try:
        s = int(sc)
        if s >= 90: return 5
        elif s >= 70: return 4
        elif s >= 50: return 2
        return 0
    except: return 0

# 2. SISTEMA DE LOGIN
if 'user' not in st.session_state:
    st.title("🏛️ Banco Central O.I.M.C.")
    user = st.selectbox("Selecciona tu cuenta", df["Usuario"].tolist())
    pin = st.text_input("Introduce tu PIN", type="password")
    if st.button("Acceder"):
        # Comprobación de PIN
        pin_real = str(df.loc[df["Usuario"] == user, "PIN"].values[0]).strip()
        if pin == pin_real:
            st.session_state.user = user
            st.rerun()
        else:
            st.error("PIN incorrecto")
else:
    u_id = st.session_state.user
    idx = df[df["Usuario"] == u_id].index[0]
    es_admin = str(df.at[idx, "Rol"]) == "admin"
    
    # 3. INTERFAZ DE CIUDADANO
    st.header(f"Hola, {u_id}")
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Saldo Disponible", f"{df.at[idx, 'Saldo']} OI")
    col_b.metric("Social Credit", f"{df.at[idx, 'SC']} pts")
    col_c.metric("Próximo Sueldo", f"{calc_sueldo(df.at[idx, 'SC'])} OI")

    # 4. FUNCIÓN DE BIZUM (TRANSFERENCIAS)
    st.divider()
    st.subheader("💸 Enviar OI (Bizum)")
    # Lista de destinatarios excluyendo al usuario actual
    destinatarios = [n for n in df["Usuario"].tolist() if n != u_id]
    dest = st.selectbox("¿A quién quieres enviar dinero?", destinatarios)
    monto = st.number_input("Cantidad de OI a enviar:", min_value=1, step=1)
    
    if st.button("Confirmar Envío"):
        # Mensaje de confirmación para el usuario y aviso para Juan
        st.success(f"Solicitud enviada. {u_id}, el Gobernador Juan debe confirmar la transferencia de {monto} OI a {dest}.")
        st.info(f"🚨 **AVISO PARA JUAN:** Resta {monto} a {u_id} y súmale {monto} a {dest} en el Excel.")

    # 5. PANEL DE GOBERNADOR (EXCLUSIVO PARA JUAN)
    if es_admin:
        st.divider()
        st.header("👑 Herramientas de Gobernador (Juan)")
        
        ciudadano = st.selectbox("Seleccionar Ciudadano para gestionar:", df["Usuario"].tolist())
        c_idx = df[df["Usuario"] == ciudadano].index[0]
        
        tab1, tab2 = st.tabs(["💰 Sueldos e Impuestos", "⚙️ Social Credit y PIN"])
        
        with tab1:
            monto_sueldo = calc_sueldo(df.at[c_idx, "SC"])
            if st.button(f"Pagar Sueldo Automático ({monto_sueldo} OI)"):
                st.success(f"Juan, ve al Excel y súmale {monto_sueldo} OI a {ciudadano}.")
            
            st.divider()
            monto_imp = st.number_input("Monto de Impuesto:", min_value=1, key="impuesto")
            if st.button(f"Cobrar Impuesto a {ciudadano}"):
                st.error(f"Juan, en el Excel: Resta {monto_imp} a {ciudadano} y súmatelo a ti.")

        with tab2:
            nuevo_sc = st.slider("Ajustar Social Credit:", 0, 100, int(df.at[c_idx, "SC"]))
            if st.button("Guardar cambios de SC"):
                st.success(f"Juan, actualiza el SC de {ciudadano} a {nuevo_sc} en el Excel.")
            
            st.divider()
            nuevo_p = st.text_input("Nuevo PIN temporal:", max_chars=4)
            if st.button("Cambiar PIN"):
                st.info(f"Juan, cambia el PIN de {ciudadano} por {nuevo_p} en el Excel.")

    # BOTÓN DE CERRAR SESIÓN
    with st.sidebar:
        if st.button("Cerrar Sesión"):
            del st.session_state.user
            st.rerun()
