import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. CONFIGURACIÓN
st.set_page_config(page_title="O.I.M.C. Banco Central", page_icon="🏛️", layout="wide")

# 2. CONEXIÓN (Lee de los Secrets que configuraste)
conn = st.connection("gsheets", type=GSheetsConnection)

def cargar():
    return conn.read(ttl=0) # ttl=0 para que sea en tiempo real

if 'df' not in st.session_state:
    st.session_state.df = cargar()

# Tabla de sueldos de tu foto
def sueldo_sc(sc):
    if sc >= 90: return 5
    elif sc >= 70: return 4
    elif sc >= 50: return 2
    else: return 0

# 3. LOGIN
if 'user' not in st.session_state:
    st.title("🏛️ O.I.M.C. - Login")
    users = st.session_state.df["Usuario"].tolist()
    u = st.selectbox("Usuario", users)
    p = st.text_input("PIN", type="password")
    if st.button("Entrar"):
        real_p = str(st.session_state.df.loc[st.session_state.df["Usuario"] == u, "PIN"].values[0])
        if p == real_p:
            st.session_state.user = u
            st.rerun()
        else:
            st.error("PIN incorrecto")
else:
    u_id = st.session_state.user
    df = st.session_state.df
    row = df[df["Usuario"] == u_id]

    # BARRA LATERAL
    with st.sidebar:
        st.header(f"Bienvenido, {u_id}")
        if st.button("Cerrar Sesión"):
            del st.session_state.user
            st.rerun()

    # INTERFAZ PRINCIPAL
    st.title("📊 Mi Cuenta Bancaria")
    c1, c2, c3 = st.columns(3)
    mi_saldo = int(row["Saldo"].values[0])
    mi_sc = int(row["SC"].values[0])
    
    c1.metric("Saldo", f"{mi_saldo} OI")
    c2.metric("Social Credit", f"{mi_sc} SC")
    c3.metric("Sueldo Próximo", f"{sueldo_sc(mi_sc)} OI")

    # --- PODER DE GOBERNADOR ---
    if row["Rol"].values[0] == "admin":
        st.divider()
        st.header("👑 Herramientas de Gobernador")
        
        # Seleccionar a quién modificar
        target = st.selectbox("Seleccionar Ciudadano para editar", df["Usuario"].tolist())
        idx = df[df["Usuario"] == target].index[0]
        
        col_sc, col_sal = st.columns(2)
        
        # Controles directos
        nuevo_sc = col_sc.slider(f"Ajustar SC de {target}", 0, 100, int(df.at[idx, "SC"]))
        nuevo_saldo = col_sal.number_input(f"Ajustar Saldo de {target}", value=int(df.at[idx, "Saldo"]))
        
        if st.button(f"GUARDAR CAMBIOS PARA {target}"):
            df.at[idx, "SC"] = nuevo_sc
            df.at[idx, "Saldo"] = nuevo_saldo
            # ESTA ES LA MAGIA: Actualiza el Google Sheets directamente
            conn.update(data=df)
            st.success("¡Datos actualizados en la nube!")
            st.session_state.df = df
            st.rerun()

        if st.button("PAGAR SUELDOS A TODOS"):
            for i, r in df.iterrows():
                df.at[i, "Saldo"] += sueldo_sc(r["SC"])
            conn.update(data=df)
            st.success("Nóminas pagadas.")
            st.session_state.df = df
            st.rerun()
