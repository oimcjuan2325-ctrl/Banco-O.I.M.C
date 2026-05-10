import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Banco Central O.I.M.C.", layout="centered")

# 1. CONEXIÓN Y DATOS
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(ttl=0)
df.columns = df.columns.str.strip() # Limpia espacios en nombres de columnas

# Función para calcular sueldo según Social Credit (SC)
def calc_sueldo(sc):
    try:
        sc = int(sc)
        if sc >= 90: return 5
        elif sc >= 70: return 4
        elif sc >= 50: return 2
        else: return 0
    except: return 0

# 2. SISTEMA DE LOGIN
if 'user' not in st.session_state:
    st.title("🏛️ Banco Central O.I.M.C.")
    
    # Lista de usuarios desde el Excel
    usuarios_list = df['Usuario'].tolist()
    user_input = st.selectbox("Selecciona tu cuenta", usuarios_list)
    pin_input = st.text_input("Introduce tu PIN", type="password")
    
    if st.button("Acceder"):
        # Buscamos el PIN en el Excel y lo limpiamos
        idx = df[df['Usuario'] == user_input].index[0]
        pin_real = str(df.at[idx, 'PIN']).split('.')[0].strip()
        
        if pin_real == str(pin_input).strip():
            st.session_state.user = user_input
            st.rerun()
        else:
            st.error("PIN incorrecto")

else:
    # 3. INTERFAZ DE USUARIO LOGUEADO
    u_id = st.session_state.user
    idx = df[df['Usuario'] == u_id].index[0]
    
    st.header(f"Hola, {u_id} 👋")
    
    # Métricas principales
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Saldo Disponible", f"{df.at[idx, 'Saldo']} OI")
    col_b.metric("Social Credit", f"{df.at[idx, 'SC']} pts")
    proximo_sueldo = calc_sueldo(df.at[idx, 'SC'])
    col_c.metric("Próximo Sueldo", f"{proximo_sueldo} OI")

    st.divider()

    # 4. FUNCIÓN DE BIZUM (TRANSFERENCIAS)
    st.subheader("💸 Enviar OI (Bizum)")
    destinatarios = [u for u in df['Usuario'].tolist() if u != u_id]
    dest = st.selectbox("¿A quién quieres enviar dinero?", destinatarios)
    monto = st.number_input("Cantidad de OI a enviar", min_value=1, step=1)
    
    if st.button("Confirmar Envío"):
        st.success(f"Solicitud enviada. El Gobernador debe confirmar la transferencia de {monto} OI.")
        st.info(f"**AVISO PARA EL GOBERNADOR:** Resta {monto} a {u_id} y súmale {monto} a {dest} en el Excel.")

    # 5. PANEL DE GOBERNADOR (Solo para Juan/Admin)
    es_admin = str(df.at[idx, 'Rol']).strip().lower() == "admin"
    if es_admin:
        st.divider()
        st.header("👑 Herramientas de Gobernador")
        
        ciudadano = st.selectbox("Seleccionar Ciudadano para gestionar:", df['Usuario'].tolist())
        c_idx = df[df['Usuario'] == ciudadano].index[0]
        
        tab1, tab2 = st.tabs(["💰 Sueldos e Impuestos", "⚙️ Social Credit y PIN"])
        
        with tab1:
            monto_sueldo = calc_sueldo(df.at[c_idx, 'SC'])
            if st.button(f"Pagar Sueldo Automático ({monto_sueldo} OI)"):
                st.success(f"¡Juan, ve al Excel y súmale {monto_sueldo} OI a {ciudadano}!")
            
            monto_imp = st.number_input("Monto de Impuesto", min_value=1)
            if st.button(f"Cobrar Impuesto a {ciudadano}"):
                st.error(f"¡Juan, en el Excel: Resta {monto_imp} a {ciudadano} y súmatelo a ti!")

        with tab2:
            nuevo_sc = st.slider("Ajustar Social Credit", 0, 100, int(df.at[c_idx, 'SC']))
            if st.button("Guardar cambios de SC"):
                st.success(f"¡Juan, actualiza el SC de {ciudadano} a {nuevo_sc} en el Excel!")
            
            nuevo_p = st.text_input("Nuevo PIN temporal", max_chars=4)
            if st.button("Cambiar PIN"):
                st.info(f"¡Juan, cambia el PIN de {ciudadano} por {nuevo_p} en el Excel!")

    # BOTÓN CERRAR SESIÓN
    if st.sidebar.button("Cerrar Sesión"):
        del st.session_state.user
        st.rerun()
