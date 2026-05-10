import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. CONFIGURACIÓN
st.set_page_config(page_title="O.I.M.C. Banco Central", page_icon="🏛️", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

def cargar_datos():
    # Cargamos todo como texto para evitar el TypeError del PIN
    data = conn.read(ttl=0)
    return data.astype(str)

if 'df' not in st.session_state:
    st.session_state.df = cargar_datos()

def calcular_sueldo_auto(sc):
    try:
        s = int(sc)
        if s >= 90: return 5
        elif s >= 70: return 4
        elif s >= 50: return 2
        else: return 0
    except: return 0

# 2. LOGIN
df = st.session_state.df.copy()

if 'user' not in st.session_state:
    st.title("🏛️ Acceso O.I.M.C.")
    u = st.selectbox("Cuenta", df["Usuario"].tolist())
    p = st.text_input("PIN", type="password")
    if st.button("Entrar"):
        if p == str(df.loc[df["Usuario"] == u, "PIN"].values[0]).strip():
            st.session_state.user = u
            st.rerun()
        else: st.error("PIN Incorrecto")
else:
    u_id = st.session_state.user
    idx_yo = df[df["Usuario"] == u_id].index[0]
    es_admin = str(df.at[idx_yo, "Rol"]) == "admin"

    # BARRA LATERAL
    with st.sidebar:
        st.header(f"👤 {u_id}")
        if st.button("Cerrar Sesión"):
            del st.session_state.user
            st.rerun()
        st.divider()
        st.subheader("🔐 Seguridad")
        n_p = st.text_input("Nuevo PIN", type="password", max_chars=4)
        if st.button("Solicitar Cambio PIN"):
            st.warning(f"AVISO: Juan, cambia el PIN de {u_id} a {n_p} en el Excel.")

    # 3. INTERFAZ
    st.title("📊 Resumen Bancario")
    c1, c2, c3 = st.columns(3)
    c1.metric("Saldo", f"{df.at[idx_yo, 'Saldo']} OI")
    c2.metric("Social Credit", f"{df.at[idx_yo, 'SC']} SC")
    c3.metric("Sueldo Próximo", f"{calcular_sueldo_auto(df.at[idx_yo, 'SC'])} OI")

    # 4. PANEL DE GOBERNADOR
    if es_admin:
        st.divider()
        st.header("👑 Herramientas de Juan")
        
        t1, t2 = st.tabs(["💰 Sueldos e Impuestos", "⚙️ Gestión Ciudadanos"])
        
        with t1:
            dest = st.selectbox("Ciudadano:", df["Usuario"].tolist())
            idx_d = df[df["Usuario"] == dest].index[0]
            s_auto = calcular_sueldo_auto(df.at[idx_d, 'SC'])
            
            st.write(f"Sueldo según SC: **{s_auto} OI**")
            if st.button(f"Pagar Sueldo a {dest}"):
                try:
                    df.at[idx_d, "Saldo"] = str(int(df.at[idx_d, "Saldo"]) + s_auto)
                    conn.update(data=df)
                    st.success("¡Pagado!")
                except:
                    st.error("Error de Google. Juan, súmale el sueldo a mano en el Excel.")
        
        with t2:
            target = st.selectbox("Editar:", df["Usuario"].tolist(), key="edit")
            idx_t = df[df["Usuario"] == target].index[0]
            n_sc = st.slider("Ajustar Social Credit", 0, 100, int(df.at[idx_t, "SC"]))
            n_sal = st.number_input("Corregir Saldo", value=int(df.at[idx_t, "Saldo"]))
            if st.button("Aplicar Cambios"):
                try:
                    df.at[idx_t, "SC"] = str(n_sc)
                    df.at[idx_t, "Saldo"] = str(n_sal)
                    conn.update(data=df)
                    st.success("Actualizado")
                except:
                    st.error("Error de permisos. Juan, haz el cambio directo en la hoja de cálculo.")

    st.divider()
    st.subheader("💸 Enviar Dinero")
    amigo = st.selectbox("Destinatario:", [n for n in df["Usuario"].tolist() if n != u_id])
    monto = st.number_input("Cantidad", min_value=1)
    if st.button("Confirmar Transferencia"):
        st.info(f"AVISO: {u_id} quiere enviar {monto} a {amigo}. Gobernador Juan, regístralo.")
