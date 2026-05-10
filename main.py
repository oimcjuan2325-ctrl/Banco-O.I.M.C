import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="O.I.M.C. Banco Central", page_icon="🏛️", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

# Función para cargar datos sin errores de tipo (TypeError)
def cargar_datos():
    data = conn.read(ttl=0)
    # Convertimos todo a 'object' para que no falle al guardar el PIN o números
    return data.astype(object)

if 'df' not in st.session_state:
    st.session_state.df = cargar_datos()

# Tabla oficial de sueldos según el Social Credit
def calcular_sueldo_auto(sc):
    try:
        sc_num = int(sc)
        if sc_num >= 90: return 5
        elif sc_num >= 70: return 4
        elif sc_num >= 50: return 2
        else: return 0
    except:
        return 0

# 2. SISTEMA DE LOGIN
df = st.session_state.df.copy()

if 'user' not in st.session_state:
    st.title("🏛️ Banco Central O.I.M.C. - Acceso")
    u = st.selectbox("Selecciona tu cuenta", df["Usuario"].tolist())
    p = st.text_input("PIN de Seguridad", type="password")
    if st.button("Entrar al Sistema"):
        p_real = str(df.loc[df["Usuario"] == u, "PIN"].values[0]).strip()
        if str(p).strip() == p_real:
            st.session_state.user = u
            st.rerun()
        else:
            st.error("PIN Incorrecto")
else:
    u_id = st.session_state.user
    idx_yo = df[df["Usuario"] == u_id].index[0]
    es_admin = str(df.at[idx_yo, "Rol"]) == "admin"

    # BARRA LATERAL (SEGURIDAD Y CIERRE)
    with st.sidebar:
        st.header(f"👤 {u_id}")
        if st.button("Cerrar Sesión"):
            del st.session_state.user
            st.rerun()
        st.divider()
        st.subheader("🔐 Seguridad")
        n_p = st.text_input("Nuevo PIN (4 cifras)", type="password", max_chars=4)
        if st.button("Guardar Nuevo PIN"):
            if n_p:
                df.at[idx_yo, "PIN"] = str(n_p)
                conn.update(data=df)
                st.session_state.df = df
                st.success("¡PIN actualizado con éxito!")
                st.rerun()

    # 3. INTERFAZ PRINCIPAL (LO QUE VE TODO EL MUNDO)
    st.title("📊 Mi Estado de Cuenta")
    col1, col2, col3 = st.columns(3)
    
    mi_saldo = int(df.at[idx_yo, "Saldo"])
    mi_sc = int(df.at[idx_yo, "SC"])
    mi_proximo_pago = calcular_sueldo_auto(mi_sc)
    
    col1.metric("Saldo Disponible", f"{mi_saldo} OI")
    col2.metric("Social Credit", f"{mi_sc} SC")
    col3.metric("Sueldo Próximo", f"{mi_proximo_pago} OI")

    # 4. PANEL DE GOBERNADOR (EXCLUSIVO PARA JUAN)
    if es_admin:
        st.divider()
        st.header("👑 Panel de Control del Gobernador")
        
        # Pestañas para organizar el poder
        t_pagos, t_gestion, t_impuestos = st.tabs(["💰 Pagar Sueldos", "⚙️ Gestión de Ciudadanos", "⚖️ Impuestos"])
        
        with t_pagos:
            st.subheader("Reparto de Nóminas Automático")
            receptor = st.selectbox("Ciudadano a pagar:", df["Usuario"].tolist())
            idx_r = df[df["Usuario"] == receptor].index[0]
            sc_receptor = int(df.at[idx_r, "SC"])
            cantidad_a_pagar = calcular_sueldo_auto(sc_receptor)
            
            st.info(f"El ciudadano {receptor} tiene {sc_receptor} SC. Sueldo automático: **{cantidad_a_pagar} OI**")
            if st.button(f"Enviar Pago de {cantidad_a_pagar} OI"):
                df.at[idx_r, "Saldo"] = int(df.at[idx_r, "Saldo"]) + cantidad_a_pagar
                conn.update(data=df)
                st.session_state.df = df
                st.success(f"Nómina enviada a {receptor}")
                st.rerun()

        with t_gestion:
            st.subheader("Modificar Estatus Social")
            target = st.selectbox("Seleccionar Ciudadano:", df["Usuario"].tolist(), key="target_edit")
            idx_t = df[df["Usuario"] == target].index[0]
            
            # Aquí puedes cambiar el SC y el Saldo directamente
            nuevo_sc = st.slider(f"Cambiar Social Credit de {target}", 0, 100, int(df.at[idx_t, "SC"]))
            nuevo_saldo_manual = st.number_input(f"Corregir Saldo de {target}", value=int(df.at[idx_t, "Saldo"]))
            
            if st.button(f"Aplicar Cambios a {target}"):
                df.at[idx_t, "SC"] = nuevo_sc
                df.at[idx_t, "Saldo"] = nuevo_saldo_manual
                conn.update(data=df)
                st.session_state.df = df
                st.success(f"Estatus de {target} actualizado.")
                st.rerun()

        with t_impuestos:
            st.subheader("Cobro de Impuestos")
            victima = st.selectbox("Cobrar a:", df["Usuario"].tolist(), key="recaudar")
            idx_v = df[df["Usuario"] == victima].index[0]
            monto_impuesto = st.number_input("Cantidad de OI a recaudar:", min_value=1, step=1)
            
            if st.button("Ejecutar Cobro"):
                df.at[idx_v, "Saldo"] = int(df.at[idx_v, "Saldo"]) - monto_impuesto
                df.at[idx_yo, "Saldo"] = int(df.at[idx_yo, "Saldo"]) + monto_impuesto
                conn.update(data=df)
                st.session_state.df = df
                st.warning(f"Se han recaudado {monto_impuesto} OI para el Tesoro Nacional")
                st.rerun()

    # 5. TRANSFERENCIAS ENTRE CIUDADANOS
    st.divider()
    st.header("💸 Enviar Fondos")
    destinatario = st.selectbox("Enviar a:", [n for n in df["Usuario"].tolist() if n != u_id])
    monto_envio = st.number_input("Cantidad a transferir:", min_value=1, max_value=max(1, mi_saldo), step=1)
    
    if st.button("Confirmar Transferencia"):
        idx_dest = df[df["Usuario"] == destinatario].index[0]
        df.at[idx_yo, "Saldo"] = int(df.at[idx_yo, "Saldo"]) - monto_envio
        df.at[idx_dest, "Saldo"] = int(df.at[idx_dest, "Saldo"]) + monto_envio
        conn.update(data=df)
        st.session_state.df = df
        st.success(f"Has enviado {monto_envio} OI a {destinatario}")
        st.rerun()
