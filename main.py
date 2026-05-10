import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. CONFIGURACIÓN
st.set_page_config(page_title="O.I.M.C. Banco", page_icon="🏛️")
conn = st.connection("gsheets", type=GSheetsConnection)

# Cargar datos asegurando que el PIN sea siempre texto para evitar el TypeError
def cargar():
    data = conn.read(ttl=0)
    data['PIN'] = data['PIN'].astype(str) # Forzamos PIN a texto
    return data

if 'df' not in st.session_state:
    st.session_state.df = cargar()

# 2. LOGIN
if 'user' not in st.session_state:
    st.title("🏛️ Acceso O.I.M.C.")
    u = st.selectbox("Usuario", st.session_state.df["Usuario"].tolist())
    p = st.text_input("PIN", type="password")
    if st.button("Entrar"):
        real_p = str(st.session_state.df.loc[st.session_state.df["Usuario"] == u, "PIN"].values[0])
        if p == real_p:
            st.session_state.user = u
            st.rerun()
else:
    u_id = st.session_state.user
    df = st.session_state.df.copy() # Usamos una copia para evitar errores
    idx_yo = df[df["Usuario"] == u_id].index[0]

    # BARRA LATERAL (CERRAR Y PIN)
    with st.sidebar:
        st.write(f"Conectado como: **{u_id}**")
        if st.button("Cerrar Sesión"):
            del st.session_state.user
            st.rerun()
        st.divider()
        st.subheader("🔐 Seguridad")
        n_p = st.text_input("Nuevo PIN", type="password", max_chars=4)
        if st.button("Actualizar PIN"):
            if n_p:
                df.at[idx_yo, "PIN"] = str(n_p)
                conn.update(data=df)
                st.session_state.df = df
                st.success("¡PIN guardado!")
                st.rerun()

    # 3. INTERFAZ PRINCIPAL
    st.title(f"Saldo: {int(df.at[idx_yo, 'Saldo'])} OI")
    st.subheader(f"Social Credit: {int(df.at[idx_yo, 'SC'])}")

    st.divider()

    # COBRAR IMPUESTO (SOLO JUAN)
    if df.at[idx_yo, "Rol"] == "admin":
        st.header("👑 Panel de Gobernador")
        
        with st.expander("⚖️ Cobrar Impuesto Rápido"):
            victima = st.selectbox("Ciudadano:", df["Usuario"].tolist())
            cuanto = st.number_input("OI a recaudar:", min_value=1, step=1)
            if st.button("¡COBRAR IMPUESTO!"):
                idx_v = df[df["Usuario"] == victima].index[0]
                df.at[idx_v, "Saldo"] -= cuanto
                df.at[idx_yo, "Saldo"] += cuanto
                conn.update(data=df)
                st.session_state.df = df
                st.warning(f"Recaudados {cuanto} OI de {victima}")
                st.rerun()

        with st.expander("⚙️ Editar Social Credit / Saldo"):
            target = st.selectbox("Editar a:", df["Usuario"].tolist())
            it = df[df["Usuario"] == target].index[0]
            n_sc = st.slider("Nuevo SC", 0, 100, int(df.at[it, "SC"]))
            n_sa = st.number_input("Nuevo Saldo", value=int(df.at[it, "Saldo"]))
            if st.button("Guardar Cambios"):
                df.at[it, "SC"] = n_sc
                df.at[it, "Saldo"] = n_sa
                conn.update(data=df)
                st.session_state.df = df
                st.success("Actualizado")
                st.rerun()
    
    st.divider()
    # TRANSFERENCIAS (PARA TODOS)
    st.header("💸 Enviar Dinero")
    dest = st.selectbox("Enviar a:", [n for n in df["Usuario"].tolist() if n != u_id])
    cant = st.number_input("Cantidad", min_value=1, max_value=int(df.at[idx_yo, "Saldo"]), step=1)
    if st.button("Enviar OI"):
        idx_d = df[df["Usuario"] == dest].index[0]
        df.at[idx_yo, "Saldo"] -= cant
        df.at[idx_d, "Saldo"] += cant
        conn.update(data=df)
        st.session_state.df = df
        st.success(f"Enviado con éxito a {dest}")
        st.rerun()
