import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import math

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="O.I.M.C. Banco Real", page_icon="🏛️", layout="wide")

# 2. CONEXIÓN A GOOGLE SHEETS
# PEGA AQUÍ TU ENLACE DE GOOGLE SHEETS
url = "https://docs.google.com/spreadsheets/d/1tfFblkVs5AcPGQFXHIv9lHE2I8MKvZTc-yApAnEWKRc/edit?usp=sharing"
conn = st.connection("gsheets", type=GSheetsConnection)

def cargar_datos():
    # Lee la hoja de cálculo
    return conn.read(spreadsheet=url, ttl="0s")

def actualizar_bd(df):
    # Guarda los cambios en Google Sheets
    conn.update(spreadsheet=url, data=df)
    st.cache_data.clear()

# Cargar datos en la sesión
if 'df' not in st.session_state:
    st.session_state.df = cargar_datos()

# Lógica salarial
def calcular_sueldo(sc):
    if sc >= 90: return 5
    elif sc >= 70: return 4
    elif sc >= 50: return 2
    else: return 0

# 3. LOGIN
if 'logeado' not in st.session_state:
    st.title("🏛️ O.I.M.C. - Iniciar Sesión")
    lista_usuarios = st.session_state.df["Usuario"].tolist()
    nombre_login = st.selectbox("Selecciona tu cuenta", lista_usuarios)
    pin_login = st.text_input("Introduce tu PIN", type="password")
    
    if st.button("Acceder"):
        pin_real = str(st.session_state.df.loc[st.session_state.df["Usuario"] == nombre_login, "PIN"].values[0])
        if pin_login == pin_real:
            st.session_state.logeado = nombre_login
            st.rerun()
        else:
            st.error("PIN incorrecto.")
else:
    u_id = st.session_state.logeado
    # Obtener fila del usuario actual
    user_row = st.session_state.df[st.session_state.df["Usuario"] == u_id]

    # BARRA LATERAL
    with st.sidebar:
        st.title(f"👤 {u_id}")
        if st.button("Cerrar Sesión"):
            del st.session_state.logeado
            st.rerun()
        st.divider()
        nuevo_pin = st.text_input("Cambiar PIN", type="password", max_chars=4)
        if st.button("Actualizar PIN"):
            st.session_state.df.loc[st.session_state.df["Usuario"] == u_id, "PIN"] = nuevo_pin
            actualizar_bd(st.session_state.df)
            st.success("PIN guardado en la nube.")

    # CUERPO PRINCIPAL
    st.title("📊 Mi Cuenta Bancaria")
    
    col1, col2, col3 = st.columns(3)
    saldo = int(user_row["Saldo"].values[0])
    sc = int(user_row["SC"].values[0])
    sueldo_prev = calcular_sueldo(sc)
    
    col1.metric("Saldo Disponible", f"{saldo} OI")
    col2.metric("Social Credit", f"{sc} SC")
    col3.metric("Sueldo Próximo", f"{sueldo_prev} OI")

    st.divider()

    # ENVIAR FONDOS
    st.subheader("💸 Enviar Fondos")
    destinatario = st.selectbox("Enviar a:", [n for n in st.session_state.df["Usuario"].tolist() if n != u_id])
    cantidad = st.number_input("Cantidad", min_value=1, max_value=max(1, saldo), step=1)
    
    if st.button("Confirmar Envío"):
        if saldo >= cantidad:
            # Restar al emisor y sumar al receptor en el DataFrame
            st.session_state.df.loc[st.session_state.df["Usuario"] == u_id, "Saldo"] -= cantidad
            st.session_state.df.loc[st.session_state.df["Usuario"] == destinatario, "Saldo"] += cantidad
            actualizar_bd(st.session_state.df)
            st.success(f"Transferencia de {cantidad} OI enviada y guardada.")
            st.rerun()

    # HERRAMIENTAS DE JUAN (ADMIN)
    rol = user_row["Rol"].values[0]
    if rol == "admin":
        st.divider()
        st.header("👑 Herramientas de Gobernador")
        accion = st.radio("Acción:", ["Pagar Sueldos", "Cobrar Impuestos", "Cambiar SC"], horizontal=True)

        if accion == "Pagar Sueldos":
            if st.button("PAGAR NÓMINAS GLOBALES"):
                for index, row in st.session_state.df.iterrows():
                    pago = calcular_sueldo(row["SC"])
                    st.session_state.df.at[index, "Saldo"] += pago
                actualizar_bd(st.session_state.df)
                st.success("Sueldos pagados y guardados en Google Sheets.")
                st.rerun()

        elif accion == "Cobrar Impuestos":
            sujeto = st.selectbox("Cobrar a:", [n for n in st.session_state.df["Usuario"].tolist() if n != "Juan"])
            monto = st.number_input("Monto", min_value=1, value=1, step=1)
            if st.button(f"Cobrar a {sujeto}"):
                st.session_state.df.loc[st.session_state.df["Usuario"] == sujeto, "Saldo"] -= monto
                st.session_state.df.loc[st.session_state.df["Usuario"] == "Juan", "Saldo"] += monto
                actualizar_bd(st.session_state.df)
                st.warning(f"Impuesto recaudado para el tesoro.")
                st.rerun()

        elif accion == "Cambiar SC":
            sujeto_sc = st.selectbox("Elegir ciudadano:", st.session_state.df["Usuario"].tolist())
            sc_actual_val = int(st.session_state.df.loc[st.session_state.df["Usuario"] == sujeto_sc, "SC"].values[0])
            nuevo_sc = st.slider("Nuevo SC", 0, 100, sc_actual_val)
            if st.button("Actualizar Estatus"):
                st.session_state.df.loc[st.session_state.df["Usuario"] == sujeto_sc, "SC"] = nuevo_sc
                actualizar_bd(st.session_state.df)
                st.success("Estatus actualizado.")
                st.rerun()
