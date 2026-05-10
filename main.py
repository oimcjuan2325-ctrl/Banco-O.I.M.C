import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. CONFIGURACIÓN
st.set_page_config(page_title="O.I.M.C. Banco Central", page_icon="🏛️", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

def cargar_limpio():
    data = conn.read(ttl=0)
    data['PIN'] = data['PIN'].astype(str) # Evita el TypeError del PIN
    return data

if 'df' not in st.session_state:
    st.session_state.df = cargar_limpio()

# Lógica oficial de sueldos según SC
def calcular_pago(sc):
    if sc >= 90: return 5
    elif sc >= 70: return 4
    elif sc >= 50: return 2
    else: return 0

# 2. SISTEMA DE LOGIN
df = st.session_state.df.copy()

if 'user' not in st.session_state:
    st.title("🏛️ Acceso al Banco O.I.M.C.")
    u = st.selectbox("Selecciona tu cuenta", df["Usuario"].tolist())
    p = st.text_input("Introduce PIN", type="password")
    if st.button("Acceder"):
        p_real = str(df.loc[df["Usuario"] == u, "PIN"].values[0]).strip()
        if str(p).strip() == p_real:
            st.session_state.user = u
            st.rerun()
        else:
            st.error("PIN incorrecto")
else:
    u_id = st.session_state.user
    idx_yo = df[df["Usuario"] == u_id].index[0]
    es_admin = df.at[idx_yo, "Rol"] == "admin"

    # BARRA LATERAL
    with st.sidebar:
        st.header(f"👤 {u_id}")
        if st.button("Cerrar Sesión"):
            del st.session_state.user
            st.rerun()
        st.divider()
        st.subheader("🔐 Seguridad")
        n_p = st.text_input("Cambiar PIN", type="password", max_chars=4)
        if st.button("Guardar Nuevo PIN"):
            df.at[idx_yo, "PIN"] = str(n_p)
            conn.update(data=df)
            st.session_state.df = df
            st.success("PIN actualizado")

    # 3. INTERFAZ DE CIUDADANO
    st.title("📊 Resumen de Cuenta")
    c1, c2, c3 = st.columns(3)
    
    saldo_actual = int(df.at[idx_yo, "Saldo"])
    sc_actual = int(df.at[idx_yo, "SC"])
    sueldo_futuro = calcular_pago(sc_actual)
    
    c1.metric("Saldo Disponible", f"{saldo_actual} OI")
    c2.metric("Social Credit", f"{sc_actual} SC")
    c3.metric("Sueldo Próximo", f"{sueldo_futuro} OI")

    st.divider()

    # 4. PANEL DE GOBERNADOR (JUAN)
    if es_admin:
        st.header("👑 Herramientas de Gobernador")
        
        tab1, tab2, tab3 = st.tabs(["💸 Pagar Sueldos", "⚖️ Impuestos", "⚙️ Gestión SC/Saldo"])
        
        with tab1:
            st.subheader("Reparto de Nóminas")
            receptor = st.selectbox("Ciudadano a pagar:", df["Usuario"].tolist())
            idx_r = df[df["Usuario"] == receptor].index[0]
            pago_auto = calcular_pago(df.at[idx_r, "SC"])
            
            st.info(f"Este ciudadano tiene {df.at[idx_r, 'SC']} SC. Le corresponden: **{pago_auto} OI**")
            if st.button(f"Enviar Sueldo a {receptor}"):
                df.at[idx_r, "Saldo"] = int(df.at[idx_r, "Saldo"]) + pago_auto
                conn.update(data=df)
                st.session_state.df = df
                st.success(f"Pagados {pago_auto} OI a {receptor}")
                st.rerun()

        with tab2:
            st.subheader("Recaudación del Estado")
            victima = st.selectbox("Cobrar impuesto a:", df["Usuario"].tolist(), key="v")
            monto = st.number_input("Cantidad:", min_value=1, step=1)
            if st.button("Cobrar Impuesto"):
                idx_v = df[df["Usuario"] == victima].index[0]
                df.at[idx_v, "Saldo"] = int(df.at[idx_v, "Saldo"]) - monto
                df.at[idx_yo, "Saldo"] = int(df.at[idx_yo, "Saldo"]) + monto
                conn.update(data=df)
                st.session_state.df = df
                st.warning(f"Recaudados {monto} de {victima}")
                st.rerun()

        with tab3:
            st.subheader("Modificar Ciudadano")
            target = st.selectbox("Persona:", df["Usuario"].tolist(), key="t")
            it = df[df["Usuario"] == target].index[0]
            
            nuevo_sc = st.slider("Cambiar Social Credit", 0, 100, int(df.at[it, "SC"]))
            nuevo_sal = st.number_input("Corregir Saldo Manual", value=int(df.at[it, "Saldo"]))
            
            if st.button("Guardar Cambios"):
                df.at[it, "SC"] = nuevo_sc
                df.at[it, "Saldo"] = nuevo_sal
                conn.update(data=df)
                st.session_state.df = df
                st.success("Estatus actualizado")
                st.rerun()

    # 5. TRANSFERENCIAS NORMALES
    st.divider()
    st.header("💸 Enviar OI")
    dest = st.selectbox("Enviar a:", [n for n in df["Usuario"].tolist() if n != u_id])
    cant = st.number_input("Cantidad a enviar:", min_value=1, max_value=max(1, saldo_actual), step=1)
    if st.button("Confirmar Transferencia"):
        idx_d = df[df["Usuario"] == dest].index[0]
        df.at[idx_yo, "Saldo"] = int(df.at[idx_yo, "Saldo"]) - cant
        df.at[idx_d, "Saldo"] = int(df.at[idx_d, "Saldo"]) + cant
        conn.update(data=df)
        st.session_state.df = df
        st.success("Dinero enviado")
        st.rerun()
