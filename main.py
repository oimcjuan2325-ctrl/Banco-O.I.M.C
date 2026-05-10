import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. CONFIGURACIÓN
st.set_page_config(page_title="O.I.M.C. Banco Central", page_icon="🏛️", layout="wide")

# 2. CONEXIÓN (Usa los Secrets configurados en Streamlit Cloud)
conn = st.connection("gsheets", type=GSheetsConnection)

def cargar_datos():
    return conn.read(ttl=0)

if 'df' not in st.session_state:
    st.session_state.df = cargar_datos()

# Tabla de sueldos según tu foto
def calcular_sueldo(sc):
    if sc >= 90: return 5
    elif sc >= 70: return 4
    elif sc >= 50: return 2
    else: return 0

# 3. LOGIN
if 'user' not in st.session_state:
    st.title("🏛️ O.I.M.C. - Acceso Privado")
    usuarios = st.session_state.df["Usuario"].tolist()
    nombre = st.selectbox("Selecciona tu identidad", usuarios)
    pin = st.text_input("PIN de seguridad", type="password")
    
    if st.button("Entrar al Sistema"):
        fila = st.session_state.df[st.session_state.df["Usuario"] == nombre]
        if pin == str(fila["PIN"].values[0]):
            st.session_state.user = nombre
            st.rerun()
        else:
            st.error("PIN Incorrecto")
else:
    u_id = st.session_state.user
    df = st.session_state.df
    fila_user = df[df["Usuario"] == u_id]
    es_admin = fila_user["Rol"].values[0] == "admin"

    # BARRA LATERAL
    with st.sidebar:
        st.header(f"👤 {u_id}")
        if es_admin: st.subheader("👑 Rango: Gobernador")
        if st.button("Cerrar Sesión"):
            del st.session_state.user
            st.rerun()

    # INTERFAZ PRINCIPAL
    st.title("📊 Estado de Cuenta O.I.M.C.")
    
    c1, c2, c3 = st.columns(3)
    mi_saldo = int(fila_user["Saldo"].values[0])
    mi_sc = int(fila_user["SC"].values[0])
    
    c1.metric("Saldo Disponible", f"{mi_saldo} OI")
    c2.metric("Social Credit", f"{mi_sc} SC")
    c3.metric("Sueldo Próximo", f"{calcular_sueldo(mi_sc)} OI")

    st.divider()

    # --- NUEVA SECCIÓN: TRANSFERENCIAS ENTRE CIUDADANOS ---
    st.header("💸 Transferir Fondos")
    col_dest, col_cant = st.columns(2)
    
    # Lista de destinatarios (todos menos tú)
    destinatarios = [n for n in df["Usuario"].tolist() if n != u_id]
    target_transfer = col_dest.selectbox("Enviar a:", destinatarios)
    cantidad_transfer = col_cant.number_input("Cantidad de OI", min_value=1, max_value=mi_saldo if mi_saldo > 0 else 1, step=1)

    if st.button("Confirmar Transferencia"):
        if mi_saldo >= cantidad_transfer:
            idx_origen = df[df["Usuario"] == u_id].index[0]
            idx_destino = df[df["Usuario"] == target_transfer].index[0]
            
            # Restar a uno y sumar al otro
            df.at[idx_origen, "Saldo"] -= cantidad_transfer
            df.at[idx_destino, "Saldo"] += cantidad_transfer
            
            # Guardar en Google Sheets
            conn.update(data=df)
            st.success(f"¡Has enviado {cantidad_transfer} OI a {target_transfer}!")
            st.session_state.df = df
            st.rerun()
        else:
            st.error("No tienes suficiente saldo para esta operación.")

    # --- PODER DE GOBERNADOR (SOLO JUAN) ---
    if es_admin:
        st.divider()
        st.header("👑 Herramientas de Gobernador")
        
        tab1, tab2 = st.tabs(["⚙️ Gestión de Ciudadanos", "💰 Pago de Nóminas"])
        
        with tab1:
            ciudadano = st.selectbox("Seleccionar para modificar:", df["Usuario"].tolist())
            idx_c = df[df["Usuario"] == ciudadano].index[0]
            
            ca, cb = st.columns(2)
            edit_sc = ca.slider(f"Social Credit de {ciudadano}", 0, 100, int(df.at[idx_c, "SC"]))
            edit_saldo = cb.number_input(f"Saldo manual de {ciudadano}", value=int(df.at[idx_c, "Saldo"]))
            
            if st.button(f"Guardar Cambios de {ciudadano}"):
                df.at[idx_c, "SC"] = edit_sc
                df.at[idx_c, "Saldo"] = edit_saldo
                conn.update(data=df)
                st.success("Base de datos actualizada.")
                st.session_state.df = df
                st.rerun()

        with tab2:
            st.write("Presiona el botón para pagar a todos según su nivel de SC.")
            if st.button("EJECUTAR PAGO GLOBAL"):
                for i, r in df.iterrows():
                    df.at[i, "Saldo"] += calcular_sueldo(r["SC"])
                conn.update(data=df)
                st.success("Todas las nóminas han sido ingresadas.")
                st.session_state.df = df
                st.rerun()
