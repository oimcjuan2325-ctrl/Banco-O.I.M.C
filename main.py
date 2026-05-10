import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. CONFIGURACIÓN
st.set_page_config(page_title="O.I.M.C. Banco Central", page_icon="🏛️", layout="wide")

# 2. CONEXIÓN
conn = st.connection("gsheets", type=GSheetsConnection)

def cargar_datos():
    return conn.read(ttl=0)

if 'df' not in st.session_state:
    st.session_state.df = cargar_datos()

def calcular_sueldo(sc):
    if sc >= 90: return 5
    elif sc >= 70: return 4
    elif sc >= 50: return 2
    else: return 0

# 3. LOGIN
if 'user' not in st.session_state:
    st.title("🏛️ O.I.M.C. - Sistema Bancario")
    u_list = st.session_state.df["Usuario"].tolist()
    nombre = st.selectbox("Identidad", u_list)
    pin_in = st.text_input("PIN Acceso", type="password")
    if st.button("Entrar"):
        real_p = str(st.session_state.df.loc[st.session_state.df["Usuario"] == nombre, "PIN"].values[0])
        if pin_in == real_p:
            st.session_state.user = nombre
            st.rerun()
        else:
            st.error("PIN Incorrecto")
else:
    u_id = st.session_state.user
    df = st.session_state.df
    idx_yo = df[df["Usuario"] == u_id].index[0]
    es_admin = df.at[idx_yo, "Rol"] == "admin"

    # BARRA LATERAL (PIN Y CERRAR SESIÓN)
    with st.sidebar:
        st.title(f"👤 {u_id}")
        if st.button("Cerrar Sesión"):
            del st.session_state.user
            st.rerun()
        st.divider()
        st.subheader("🔐 Seguridad")
        n_pin = st.text_input("Nuevo PIN (4 dígitos)", type="password", max_chars=4)
        if st.button("Actualizar mi PIN"):
            if len(n_pin) == 4:
                df.at[idx_yo, "PIN"] = n_pin
                try:
                    conn.update(data=df)
                    st.success("¡PIN actualizado!")
                except:
                    st.warning("⚠️ Error de permiso. Juan tiene que cambiar tu PIN manualmente en el Excel.")

    # INTERFAZ
    st.title("📊 Mi Cuenta")
    c1, c2, c3 = st.columns(3)
    c1.metric("Saldo", f"{int(df.at[idx_yo, 'Saldo'])} OI")
    c2.metric("Social Credit", f"{int(df.at[idx_yo, 'SC'])} SC")
    c3.metric("Sueldo", f"{calcular_sueldo(df.at[idx_yo, 'SC'])} OI")

    st.divider()

    # TRANSFERENCIAS
    st.header("💸 Enviar Fondos")
    dest = st.selectbox("Destinatario:", [n for n in df["Usuario"].tolist() if n != u_id])
    cant = st.number_input("Cantidad", min_value=1, step=1)
    
    if st.button("Confirmar Envío"):
        if int(df.at[idx_yo, 'Saldo']) >= cant:
            idx_dest = df[df["Usuario"] == dest].index[0]
            df.at[idx_yo, "Saldo"] -= cant
            df.at[idx_dest, "Saldo"] += cant
            try:
                conn.update(data=df)
                st.success(f"Enviado con éxito a {dest}")
                st.rerun()
            except:
                st.error("❌ ERROR DE PERMISOS DE GOOGLE.")
                st.info(f"ANOTA ESTO: {u_id} ha enviado {cant} a {dest}. Juan, cámbialo a mano en el Excel.")
        else:
            st.error("Saldo insuficiente")

    # PANEL GOBERNADOR
    if es_admin:
        st.divider()
        st.header("👑 Herramientas de Juan")
        target = st.selectbox("Editar Ciudadano:", df["Usuario"].tolist())
        idx_t = df[df["Usuario"] == target].index[0]
        
        ca, cb = st.columns(2)
        nuevo_sc = ca.slider("Social Credit", 0, 100, int(df.at[idx_t, "SC"]))
        nuevo_sal = cb.number_input("Saldo Manual", value=int(df.at[idx_t, "Saldo"]))
        
        if st.button(f"Guardar Cambios de {target}"):
            df.at[idx_t, "SC"] = nuevo_sc
            df.at[idx_t, "Saldo"] = nuevo_sal
            try:
                conn.update(data=df)
                st.success("Guardado en la nube.")
                st.rerun()
            except:
                st.error("No se puede escribir en el Excel desde aquí. Hazlo a mano en la otra pestaña.")
