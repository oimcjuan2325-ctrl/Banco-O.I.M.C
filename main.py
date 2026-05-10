import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Configuración de la web
st.set_page_config(page_title="Banco Central O.I.M.C.", page_icon="🏛️")

# 1. CONEXIÓN Y LECTURA DE DATOS (ttl=0 para tiempo real)
conn = st.connection("gsheets", type=GSheetsConnection)

def cargar_datos():
    data = conn.read(ttl=0)
    data.columns = data.columns.str.strip() 
    return data

df = cargar_datos()

# Función para guardar cambios en el Excel
def guardar(nuevo_df):
    conn.update(data=nuevo_df)
    st.cache_data.clear()
    st.rerun()

# Función para calcular el sueldo semanal
def calcular_sueldo(sc_puntos):
    try:
        val = int(float(sc_puntos))
        if val >= 90: return 10
        elif val >= 70: return 7
        elif val >= 50: return 4
        else: return 0
    except: return 0

# 2. PANTALLA DE INICIO DE SESIÓN
if 'user' not in st.session_state:
    st.title("🏛️ Tu cuenta bancaria de la OIMC")
    st.subheader("Iniciar Sesión")
    
    usuarios = df['Usuario'].tolist()
    user_sel = st.selectbox("Selecciona tu cuenta", ["---"] + usuarios)
    pin_ingresado = st.text_input("Introduce tu PIN", type="password")
    
    if st.button("Acceder"):
        if user_sel != "---":
            idx = df[df['Usuario'] == user_sel].index[0]
            pin_real = str(df.at[idx, 'PIN']).split('.')[0].strip()
            if pin_real == pin_ingresado.strip():
                st.session_state.user = user_sel
                st.rerun()
            else:
                st.error("❌ PIN incorrecto")
        else:
            st.warning("Selecciona un usuario.")

# 3. INTERFAZ DE USUARIO LOGUEADO
else:
    nombre_usuario = st.session_state.user
    idx_u = df[df['Usuario'] == nombre_usuario].index[0]
    
    st.title(f"Hola, {nombre_usuario} 👋")
    
    saldo_disp = int(float(df.at[idx_u, 'Saldo']))
    sc_disp = int(float(df.at[idx_u, 'SC']))
    sueldo_sem = calcular_sueldo(sc_disp)
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Saldo", f"{saldo_disp} OI")
    c2.metric("Social Credit", f"{sc_disp} pts")
    c3.metric("Sueldo Semanal", f"{sueldo_sem} OI")

    st.divider()

    # MENÚ DE OPCIONES (He quitado la pestaña de Seguridad/PIN)
    pestanas = st.tabs(["💸 Bizum", "💵 Sacar Efectivo", "🚪 Salir"])

    with pestanas[0]: # BIZUM
        st.subheader("Enviar OI (Bizum)")
        otros = [u for u in df['Usuario'].tolist() if u != nombre_usuario]
        receptor = st.selectbox("¿A quién envías?", otros)
        cantidad = st.number_input("Cantidad a enviar", min_value=1, step=1)
        
        if st.button("Confirmar Bizum"):
            if saldo_disp >= cantidad:
                df.at[idx_u, 'Saldo'] = saldo_disp - cantidad
                idx_rec = df[df['Usuario'] == receptor].index[0]
                saldo_rec = int(float(df.at[idx_rec, 'Saldo']))
                df.at[idx_rec, 'Saldo'] = saldo_rec + cantidad
                guardar(df)
            else:
                st.error("No tienes suficiente saldo.")

    with pestanas[1]: # SACAR EFECTIVO
        st.subheader("Retirar dinero físico")
        st.info("El dinero se restará de tu cuenta digital y Juan te lo dará en mano.")
        monto_retirar = st.number_input("¿Cuánto quieres sacar?", min_value=1, step=1)
        
        if st.button("Retirar Efectivo"):
            if saldo_disp >= monto_retirar:
                df.at[idx_u, 'Saldo'] = saldo_disp - monto_retirar
                guardar(df)
                st.success(f"Has retirado {monto_retirar} OI. ¡Avisa a Juan!")
            else:
                st.error("Saldo insuficiente.")

    with pestanas[2]: # CERRAR SESIÓN
        if st.button("Finalizar Sesión"):
            del st.session_state.user
            st.rerun()

    # 4. PANEL EXCLUSIVO PARA JUAN (ADMIN)
    es_admin = str(df.at[idx_u, 'Rol']).strip().lower() == "admin"
    if es_admin:
        st.divider()
        st.header("👑 Panel de Gobernador")
        
        target = st.selectbox("Selecciona Ciudadano", df['Usuario'].tolist())
        idx_t = df[df['Usuario'] == target].index[0]
        
        admin_opciones = st.tabs(["💰 Impuestos", "⭐ Ajustar SC", "🏦 Pagar Sueldo"])
        
        with admin_opciones[0]: # COBRAR IMPUESTOS
            monto_imp = st.number_input("Cantidad de Impuesto", min_value=1, step=1)
            if st.button(f"Cobrar Impuesto a {target}"):
                saldo_t = int(float(df.at[idx_t, 'Saldo']))
                df.at[idx_t, 'Saldo'] = saldo_t - monto_imp
                saldo_juan = int(float(df.at[idx_u, 'Saldo']))
                df.at[idx_u, 'Saldo'] = saldo_juan + monto_imp
                guardar(df)

        with admin_opciones[1]: # AJUSTAR SC
            sc_actual_t = int(float(df.at[idx_t, 'SC']))
            nuevo_sc_val = st.slider("Ajustar Social Credit", 0, 100, sc_actual_t)
            if st.button("Guardar Social Credit"):
                df.at[idx_t, 'SC'] = nuevo_sc_val
                guardar(df)

        with admin_opciones[2]: # PAGAR SUELDOS
            sueldo_estado = calcular_sueldo(df.at[idx_t, 'SC'])
            if st.button(f"Pagar Sueldo Semanal ({sueldo_estado} OI)"):
                saldo_t_actual = int(float(df.at[idx_t, 'Saldo']))
                df.at[idx_t, 'Saldo'] = saldo_t_actual + sueldo_estado
                guardar(df)
