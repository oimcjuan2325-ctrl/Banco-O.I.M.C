import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Configuración de página
st.set_page_config(page_title="Banco O.I.M.C.", page_icon="🏛️")

# 1. CONEXIÓN Y CARGA DE DATOS
conn = st.connection("gsheets", type=GSheetsConnection)

def cargar_datos():
    data = conn.read(ttl=0)
    data.columns = data.columns.str.strip() # Limpia espacios
    return data

df = cargar_datos()

# Función para guardar cambios en el Excel automáticamente
def actualizar_excel(nuevo_df):
    conn.update(data=nuevo_df)
    st.cache_data.clear()

# Función para calcular sueldo por SC
def calc_sueldo(sc):
    try:
        sc_val = int(sc)
        if sc_val >= 90: return 10
        elif sc_val >= 70: return 7
        elif sc_val >= 50: return 4
        else: return 0
    except: return 0

# 2. PANTALLA DE INICIO DE SESIÓN
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
        else:
            st.warning("Selecciona un usuario")

# 3. PANEL DE USUARIO LOGUEADO
else:
    u_id = st.session_state.user
    idx = df[df['Usuario'] == u_id].index[0]
    
    st.title(f"👋 Hola, {u_id}")
    
    # Visualización de datos (Números redondos)
    col1, col2, col3 = st.columns(3)
    saldo_actual = int(float(df.at[idx, 'Saldo']))
    sc_actual = int(float(df.at[idx, 'SC']))
    
    col1.metric("Tu Saldo", f"{saldo_actual} OI")
    col2.metric("Social Credit", f"{sc_actual} pts")
    col3.metric("Sueldo Semanal", f"{calc_sueldo(sc_actual)} OI")

    st.divider()

    # OPCIONES DE USUARIO
    menu = st.tabs(["💸 Bizum", "💵 Sacar Efectivo", "🔐 Seguridad", "⚙️ Ajustes"])

    with menu[0]: # BIZUM
        st.subheader("Enviar dinero (Bizum)")
        destinatarios = [u for u in df['Usuario'].tolist() if u != u_id]
        dest = st.selectbox("¿A quién envías?", destinatarios)
        monto = st.number_input("Cantidad a enviar", min_value=1, step=1, key="bizum_val")
        
        if st.button("Confirmar Bizum"):
            if saldo_actual >= monto:
                df.at[idx, 'Saldo'] = saldo_actual - monto
                dest_idx = df[df['Usuario'] == dest].index[0]
                df.at[dest_idx, 'Saldo'] = int(float(df.at[dest_idx, 'Saldo'])) + monto
                actualizar_excel(df)
                st.success(f"✅ ¡Enviados {monto} OI a {dest}!")
                st.rerun()
            else:
                st.error("No tienes suficiente saldo.")

    with menu[1]: # SACAR EFECTIVO
        st.subheader("Retirar dinero en efectivo")
        st.info("Al sacar dinero, se restará de tu cuenta digital. Juan te entregará las OI físicas.")
        monto_cash = st.number_input("¿Cuánto quieres sacar?", min_value=1, step=1, key="cash_val")
        
        if st.button("Sacar en Efectivo"):
            if saldo_actual >= monto_cash:
                df.at[idx, 'Saldo'] = saldo_actual - monto_cash
                actualizar_excel(df)
                st.balloons()
                st.success(f"✅ Has retirado {monto_cash} OI. ¡Avisa a Juan para que te las entregue!")
                # Esto crea una nota temporal en la sesión para que Juan la vea
                if 'avisos' not in st.session_state: st.session_state.avisos = []
                st.session_state.avisos.append(f"🔔 {u_id} ha sacado {monto_cash} OI en efectivo.")
            else:
                st.error("No tienes suficiente saldo.")

    with menu[2]: # SEGURIDAD (CAMBIAR PIN)
        st.subheader("Cambiar mi PIN")
        nuevo_pin = st.text_input("Nuevo PIN (4 números)", max_chars=4, type="password")
        if st.button("Guardar nuevo PIN"):
            if len(nuevo_pin) == 4 and nuevo_pin.isdigit():
                df.at[idx, 'PIN'] = nuevo_pin
                actualizar_excel(df)
                st.success("¡PIN cambiado correctamente!")
            else:
                st.error("El PIN debe ser de 4 números.")

    with menu[3]: # CERRAR SESIÓN
        if st.button("Cerrar Sesión"):
            del st.session_state.user
            st.rerun()

    # 4. PANEL EXCLUSIVO PARA JUAN (ADMINISTRADOR)
    es_admin = str(df.at[idx, 'Rol']).strip().lower() == "admin"
    if es_admin:
        st.divider()
        st.header("👑 Panel de Administrador")
        
        # Mostrar avisos de efectivo si existen en esta sesión
        if 'avisos' in st.session_state and st.session_state.avisos:
            st.warning("⚠️ RETIRADAS PENDIENTES:")
            for aviso in st.session_state.avisos:
                st.write(aviso)
            if st.button("Limpiar Avisos"):
                st.session_state.avisos = []
                st.rerun()

        ciudadano = st.selectbox("Ciudadano a gestionar", df['Usuario'].tolist())
        c_idx = df[df['Usuario'] == ciudadano].index[0]

        admin_tabs = st.tabs(["💰 Impuestos", "⭐ Ajustar SC", "🏦 Pagar Sueldos"])

        with admin_tabs[0]: # COBRAR IMPUESTOS
            impuesto = st.number_input("Monto impuesto", min_value=1, step=1)
            if st.button(f"Cobrar a {ciudadano}"):
                df.at[c_idx, 'Saldo'] = int(float(df.at[c_idx, 'Saldo'])) - impuesto
                df.at[idx, 'Saldo'] = int(float(df.at[idx, 'Saldo'])) + impuesto
                actualizar_excel(df)
                st.success(f"Impuesto cobrado. Los {impuesto} OI han ido a tu cuenta.")
                st.rerun()

        with admin_tabs[1]: # AJUSTAR SC
            nuevo_sc = st.slider("Nivel de Social Credit", 0, 100, int(float(df.at[c_idx, 'SC'])))
            if st.button("Guardar Social Credit"):
                df.at[c_idx, 'SC'] = nuevo_sc
                actualizar_excel(df)
                st.success(f"SC de {ciudadano} actualizado a {nuevo_sc}")
                st.rerun()

        with admin_tabs[2]: # PAGAR SUELDOS
            sueldo_a_pagar = calc_sueldo(df.at[c_idx, 'SC'])
            if st.button(f"Pagar Sueldo ({sueldo_a_pagar} OI)"):
                df.at[c_idx, 'Saldo'] = int(float(df.at[c_idx, 'Saldo'])) + sueldo_a_pagar
                actualizar_excel(df)
                st.success(f"Sueldo de {sueldo_a_pagar} OI pagado a {ciudadano}.")
                st.rerun()
