import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. CONEXIÓN RÁPIDA
st.set_page_config(page_title="O.I.M.C. Banco", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(ttl=0)

# Lógica de sueldos por SC
def calc_sueldo(sc):
    s = int(sc)
    if s >= 90: return 5
    elif s >= 70: return 4
    elif s >= 50: return 2
    return 0

# 2. LOGIN
if 'user' not in st.session_state:
    st.title("🏛️ Banco O.I.M.C.")
    user = st.selectbox("Usuario", df["Usuario"].tolist())
    pin = st.text_input("PIN", type="password")
    if st.button("Entrar"):
        if pin == str(df.loc[df["Usuario"] == user, "PIN"].values[0]):
            st.session_state.user = user
            st.rerun()
else:
    u_id = st.session_state.user
    idx = df[df["Usuario"] == u_id].index[0]
    
    # DATOS DEL USUARIO
    st.header(f"Hola, {u_id}")
    st.metric("Mi Saldo", f"{df.at[idx, 'Saldo']} OI")
    st.write(f"Tu SC actual es **{df.at[idx, 'SC']}**. Cobrarás **{calc_sueldo(df.at[idx, 'SC'])} OI**.")

    # 3. PANEL DE GOBERNADOR (JUAN)
    if str(df.at[idx, "Rol"]) == "admin":
        st.divider()
        st.header("👑 Panel de Juan")
        
        # ELEGIR CIUDADANO
        target = st.selectbox("Gestionar a:", df["Usuario"].tolist())
        t_idx = df[df["Usuario"] == target].index[0]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("💰 Sueldos e Impuestos")
            op = st.radio("Acción", ["Pagar Sueldo", "Cobrar Impuesto"])
            if op == "Pagar Sueldo":
                monto = calc_sueldo(df.at[t_idx, "SC"])
                st.info(f"Sueldo automático: {monto} OI")
            else:
                monto = st.number_input("Monto Impuesto", min_value=1)
            
            if st.button("Realizar Operación"):
                st.success(f"¡Hecho! Juan, ve al Excel y cambia el saldo de {target}.")

        with col2:
            st.subheader("⚙️ Social Credit")
            nuevo_sc = st.slider("Nuevo SC", 0, 100, int(df.at[t_idx, "SC"]))
            if st.button("Cambiar SC"):
                st.success(f"Juan, ponle {nuevo_sc} de SC a {target} en el Excel.")

    # 4. CAMBIAR PIN (SIDEBAR)
    with st.sidebar:
        st.subheader("🔐 Seguridad")
        n_p = st.text_input("Nuevo PIN", max_chars=4)
        if st.button("Cambiar PIN"):
            st.info(f"Juan, cambia el PIN de {u_id} a {n_p} en el Excel.")
        if st.button("Cerrar Sesión"):
            del st.session_state.user
            st.rerun()
