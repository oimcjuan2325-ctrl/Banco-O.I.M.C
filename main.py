import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. CONFIGURACIÓN
st.set_page_config(page_title="O.I.M.C. Banco", page_icon="🏛️")
conn = st.connection("gsheets", type=GSheetsConnection)

def cargar():
    # Leemos y forzamos TODO a ser texto/número limpio para que no haya líos de tipos
    data = conn.read(ttl=0)
    return data

if 'df' not in st.session_state:
    st.session_state.df = cargar()

# 2. LOGIN
df_actual = st.session_state.df.copy()

if 'user' not in st.session_state:
    st.title("🏛️ Acceso O.I.M.C.")
    u = st.selectbox("Usuario", df_actual["Usuario"].tolist())
    p = st.text_input("PIN", type="password")
    if st.button("Entrar"):
        # Comprobación de seguridad comparando como strings
        real_p = str(df_actual.loc[df_actual["Usuario"] == u, "PIN"].values[0]).strip()
        if str(p).strip() == real_p:
            st.session_state.user = u
            st.rerun()
        else:
            st.error("PIN Incorrecto")
else:
    u_id = st.session_state.user
    idx_yo = df_actual[df_actual["Usuario"] == u_id].index[0]

    # BARRA LATERAL
    with st.sidebar:
        st.write(f"👤 **{u_id}**")
        if st.button("Cerrar Sesión"):
            del st.session_state.user
            st.rerun()
        st.divider()
        st.subheader("🔐 Cambiar PIN")
        n_p = st.text_input("Nuevo PIN", type="password", max_chars=4)
        if st.button("Guardar PIN"):
            if n_p:
                # Actualizamos el valor asegurándonos de que sea un string limpio
                df_actual.at[idx_yo, "PIN"] = str(n_p)
                conn.update(data=df_actual)
                st.session_state.df = df_actual
                st.success("¡PIN actualizado!")
                st.rerun()

    # 3. INTERFAZ PRINCIPAL
    saldo_v = df_actual.at[idx_yo, 'Saldo']
    sc_v = df_actual.at[idx_yo, 'SC']
    
    st.title(f"Saldo: {int(saldo_v)} OI")
    st.subheader(f"Social Credit: {int(sc_v)}")

    # 4. HERRAMIENTAS DE JUAN (IMPUESTOS)
    if str(df_actual.at[idx_yo, "Rol"]) == "admin":
        st.divider()
        st.header("👑 Panel de Gobernador")
        
        with st.expander("⚖️ Cobrar Impuesto"):
            victima = st.selectbox("Ciudadano:", df_actual["Usuario"].tolist())
            cuanto = st.number_input("OI a quitar:", min_value=1, step=1)
            if st.button("EJECUTAR COBRO"):
                idx_v = df_actual[df_actual["Usuario"] == victima].index[0]
                df_actual.at[idx_v, "Saldo"] = int(df_actual.at[idx_v, "Saldo"]) - cuanto
                df_actual.at[idx_yo, "Saldo"] = int(df_actual.at[idx_yo, "Saldo"]) + cuanto
                conn.update(data=df_actual)
                st.session_state.df = df_actual
                st.warning(f"Cobrado a {victima}")
                st.rerun()

    # 5. TRANSFERENCIAS
    st.divider()
    st.header("💸 Enviar Dinero")
    dest = st.selectbox("Destinatario:", [n for n in df_actual["Usuario"].tolist() if n != u_id])
    cant = st.number_input("Cantidad", min_value=1, max_value=int(saldo_v), step=1)
    if st.button("Enviar Fondos"):
        idx_d = df_actual[df_actual["Usuario"] == dest].index[0]
        df_actual.at[idx_yo, "Saldo"] = int(df_actual.at[idx_yo, "Saldo"]) - cant
        df_actual.at[idx_d, "Saldo"] = int(df_actual.at[idx_d, "Saldo"]) + cant
        conn.update(data=df_actual)
        st.session_state.df = df_actual
        st.success(f"¡Enviado a {dest}!")
        st.rerun()
