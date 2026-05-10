import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Configuración de página
st.set_page_config(page_title="Banco O.I.M.C.", page_icon="🏛️")

# 1. CONEXIÓN Y CARGA DE DATOS (ttl=0 para evitar que se quede pillado el saldo)
conn = st.connection("gsheets", type=GSheetsConnection)

def cargar_datos():
    # El ttl=0 es la clave para que lea el Excel en tiempo real
    data = conn.read(ttl=0)
    data.columns = data.columns.str.strip() 
    return data

df = cargar_datos()

# Función para guardar cambios y FORZAR actualización visual
def actualizar_y_recargar(nuevo_df):
    conn.update(data=nuevo_df)
    st.cache_data.clear() # Borra la memoria temporal
    st.rerun() # Reinicia la web para mostrar los nuevos datos

# Función para calcular sueldo por SC
def calc_sueldo(sc):
    try:
        sc_val = int(float(sc))
        if sc_val >= 90: return 10
        elif sc_val >= 70: return 7
        elif sc_val >= 50: return 4
        else: return 0
    except: return 0

# 2. LOGIN
if 'user' not in st.session_state:
    st.title("🏛️ Tu cuenta bancaria de la OIMC")
    st.subheader("Iniciar Sesión")
    
    user_list = df['Usuario'].tolist()
    user_input = st.selectbox("Selecciona tu cuenta", ["---"] + user_list)
    pin_input = st.text_input("Introduce tu PIN", type="password")
    
    if st.button("Entrar"):
        if user_input != "---":
            idx = df[df['Usuario'] == user_input].index[0]
            pin_real = str(df.at[idx, 'PIN']).split('.')[0].strip()
            if pin_real == pin_input.strip():
                st.session_state.user = user_input
                st.rerun()
            else:
                st.error("❌ PIN incorrecto")

# 3. PANEL DE USUARIO
else:
    u_id = st.session_state.user
    # Volvemos a buscar el índice por si los datos han cambiado
    idx = df[df['Usuario'] == u_id].index[0]
    
    st.title(f"👋 Hola, {u_id}")
    
    # Datos en números redondos
    saldo_actual = int(float(df.at[idx, 'Saldo']))
    sc_actual = int(float(df.at[idx, 'SC']))
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Tu Saldo", f"{saldo_actual} OI")
    col2.metric("Social Credit", f"{sc_actual} pts")
    col3.metric("Sueldo Semanal", f"{calc_sueldo(sc_actual)} OI")

    st.divider()

    menu = st.tabs(["💸 Bizum", "💵 Sacar Efectivo", "🔐 Seguridad", "⚙️ Ajustes"])

    with menu[0]: # BIZUM
        destinatarios = [u for u in df['Usuario'].tolist() if u != u_id]
        dest = st.selectbox("¿A quién envías?", destinatarios)
        monto = st.number_input("Cantidad", min_value=1, step=1, key="bz")
        if st.button("Confirmar Bizum"):
            if saldo_actual >= monto:
                df.at[idx, 'Saldo'] = saldo_actual - monto
                dest_idx = df[df['Usuario'] == dest].index[0]
                df.at[dest_idx, 'Saldo'] = int(float(df.at[dest_idx, 'Saldo'])) + monto
                actualizar_y_recargar(df)
            else:
                st.error("Saldo insuficiente")

    with menu[1]: # SACAR EFECTIVO (Arreglado)
        st.info("El dinero se restará de tu cuenta ahora y Juan te lo dará en físico.")
        monto_cash = st.number_input("Cantidad a retirar", min_value=1, step=1, key="cs")
        if st.button("Sacar en Efectivo"):
            if saldo_actual >= monto_cash:
                # Restamos y enviamos al Excel inmediatamente
                df.at[idx, 'Saldo'] = saldo_actual - monto_cash
                actualizar_y_recargar(df)
                st.success("¡Hecho! Avisa a Juan.")
            else:
                st.error("Saldo insuficiente")

    with menu[2]: # CAMBIAR PIN
        nuevo_pin = st.text_input("Nuevo PIN", max_chars=4, type="password")
        if st.button("Guardar PIN"):
            if len(nuevo_pin) == 4:
                df.at[idx, 'PIN'] = nuevo_pin
                actualizar_y_recargar(df)

    with menu[3]:
        if st.button("Cerrar Sesión"):
            del st.session_state.user
            st.rerun()

    # 4. PANEL JUAN (ADMIN)
    if str(df.at[idx, 'Rol']).strip().lower() == "admin":
        st.divider()
        st.header("👑 Panel de Gobernador")
        ciudadano = st.selectbox("Gestionar ciudadano:", df['Usuario'].tolist())
        c_idx = df[df['Usuario'] == ciudadano].index[0]
        
        adm_tabs = st.tabs(["💰 Impuestos", "⭐ Social Credit", "🏦 Sueldos"])
        
        with adm_tabs[0]: # IMPUESTOS
            m_imp = st.number_input("Monto", min_value=1, step=1)
            if st.button(f"Cobrar a {ciudadano}"):
                df.at[c_idx, 'Saldo'] = int(float(df.at[c_idx, 'Saldo'])) - m_imp
                df.at[idx, 'Saldo'] = int(float(df.at[idx, 'Saldo'])) + m_imp
                actualizar_y_recargar(df)

        with adm_tabs[1]: # SC
            n_sc = st.slider("Nivel", 0, 100, int(float(df.at[c_idx, 'SC'])))
            if st.button("Actualizar SC"):
                df.at[c_idx, 'SC'] = n_sc
                actualizar_y_recargar(df)

        with adm_tabs[2]: # SUELDOS
            s_pagar = calc_sueldo(df.at[c_idx, 'SC'])
            if st.button(f"Pagar {s_pagar} OI"):
                df.at[c_idx, 'Saldo'] = int(float(df.at[c_idx, 'Saldo'])) + s_pagar
                actualizar_y_recargar(df)
