import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. CONFIGURACIÓN BÁSICA
st.set_page_config(page_title="O.I.M.C. Banco", page_icon="🏛️")
conn = st.connection("gsheets", type=GSheetsConnection)

def cargar():
    return conn.read(ttl=0)

if 'df' not in st.session_state:
    st.session_state.df = cargar()

# 2. LOGIN SIMPLE
if 'user' not in st.session_state:
    st.title("🏛️ O.I.M.C. Acceso")
    u = st.selectbox("Usuario", st.session_state.df["Usuario"].tolist())
    p = st.text_input("PIN", type="password")
    if st.button("Entrar"):
        real_p = str(st.session_state.df.loc[st.session_state.df["Usuario"] == u, "PIN"].values[0])
        if p == real_p:
            st.session_state.user = u
            st.rerun()
else:
    u_id = st.session_state.user
    df = st.session_state.df
    idx_yo = df[df["Usuario"] == u_id].index[0]

    # BARRA LATERAL
    with st.sidebar:
        st.write(f"Usuario: **{u_id}**")
        if st.button("Cerrar Sesión"):
            del st.session_state.user
            st.rerun()
        st.divider()
        # CAMBIO DE PIN
        n_p = st.text_input("Nuevo PIN", type="password", max_chars=4)
        if st.button("Cambiar PIN"):
            df.at[idx_yo, "PIN"] = n_p
            conn.update(data=df)
            st.success("PIN cambiado")

    # 3. INTERFAZ DE USUARIO
    st.title(f"Saldo: {int(df.at[idx_yo, 'Saldo'])} OI")
    st.write(f"Social Credit: {int(df.at[idx_yo, 'SC'])}")

    st.divider()

    # TRANSFERIR
    st.subheader("💸 Enviar Dinero")
    dest = st.selectbox("A quién:", [n for n in df["Usuario"].tolist() if n != u_id])
    cant = st.number_input("Cantidad", min_value=1, step=1)
    if st.button("Enviar"):
        idx_d = df[df["Usuario"] == dest].index[0]
        df.at[idx_yo, "Saldo"] -= cant
        df.at[idx_dest, "Saldo"] += cant
        conn.update(data=df)
        st.success("¡Enviado!")
        st.rerun()

    # 4. HERRAMIENTAS DE JUAN (IMPUESTOS Y EDICIÓN)
    if df.at[idx_yo, "Rol"] == "admin":
        st.divider()
        st.header("👑 Panel de Gobernador")
        
        # COBRAR IMPUESTOS (Rápido)
        st.subheader("⚖️ Cobrar Impuesto")
        victima = st.selectbox("Cobrar a:", df["Usuario"].tolist(), key="v")
        cuanto = st.number_input("Monto del impuesto", min_value=1, step=1)
        if st.button("¡COBRAR YA!"):
            idx_v = df[df["Usuario"] == victima].index[0]
            df.at[idx_v, "Saldo"] -= cuanto
            df.at[idx_yo, "Saldo"] += cuanto # Va para ti, Juan
            conn.update(data=df)
            st.warning(f"Has recaudado {cuanto} OI de {victima}")
            st.rerun()

        # EDITAR TODO
        st.subheader("⚙️ Editar Ciudadano")
        target = st.selectbox("Persona:", df["Usuario"].tolist())
        idx_t = df[df["Usuario"] == target].index[0]
        n_sc = st.slider("Social Credit", 0, 100, int(df.at[idx_t, "SC"]))
        n_sa = st.number_input("Saldo Manual", value=int(df.at[idx_t, "Saldo"]))
        if st.button("Guardar"):
            df.at[idx_t, "SC"] = n_sc
            df.at[idx_t, "Saldo"] = n_sa
            conn.update(data=df)
            st.success("Actualizado")
            st.rerun()
