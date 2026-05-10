import streamlit as st

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="O.I.M.C. Banco Central", page_icon="🏛️", layout="wide")

# 2. INICIALIZACIÓN DE LA BASE DE DATOS
if 'usuarios' not in st.session_state:
    st.session_state.usuarios = {
        "Juan": {"pin": "2325", "saldo": 10, "sc": 100, "rol": "admin"},
        "Asier": {"pin": "0000", "saldo": 10, "sc": 70, "rol": "user"},
        "Erika": {"pin": "0000", "saldo": 10, "sc": 70, "rol": "user"},
        "Nahia": {"pin": "0000", "saldo": 10, "sc": 70, "rol": "user"},
        "Gaizka": {"pin": "0000", "saldo": 10, "sc": 70, "rol": "user"},
        "Mikel": {"pin": "0000", "saldo": 10, "sc": 70, "rol": "user"},
        "Yolanda": {"pin": "0000", "saldo": 10, "sc": 70, "rol": "user"},
        "Jesús": {"pin": "0000", "saldo": 10, "sc": 70, "rol": "user"},
        "Iñaki": {"pin": "9999", "saldo": 10, "sc": 20, "rol": "user"}
    }

# Lógica para calcular sueldo según la tabla de la foto
def calcular_sueldo(sc):
    if sc >= 90: return 5
    elif sc >= 70: return 4
    elif sc >= 50: return 2
    else: return 0

# 3. LOGIN
if 'logeado' not in st.session_state:
    st.title("🏛️ O.I.M.C. - Iniciar Sesión")
    nombre_login = st.selectbox("Selecciona tu cuenta", list(st.session_state.usuarios.keys()))
    pin_login = st.text_input("Introduce tu PIN", type="password")
    if st.button("Acceder"):
        if st.session_state.usuarios[nombre_login]["pin"] == pin_login:
            st.session_state.logeado = nombre_login
            st.rerun()
        else:
            st.error("PIN incorrecto.")
else:
    u_id = st.session_state.logeado
    user_data = st.session_state.usuarios[u_id]

    # BARRA LATERAL
    with st.sidebar:
        st.title(f"👤 {u_id}")
        if st.button("Cerrar Sesión"):
            del st.session_state.logeado
            st.rerun()
        st.divider()
        st.subheader("⚙️ Configuración")
        nuevo_pin = st.text_input("Cambiar PIN", type="password", max_chars=4)
        if st.button("Actualizar PIN"):
            st.session_state.usuarios[u_id]["pin"] = nuevo_pin
            st.success("PIN actualizado.")

    # CUERPO PRINCIPAL
    st.title("📊 Mi Cuenta Bancaria")
    
    col1, col2, col3 = st.columns(3)
    saldo_actual = st.session_state.usuarios[u_id]["saldo"]
    sc_actual = st.session_state.usuarios[u_id]["sc"]
    sueldo_prev = calcular_sueldo(sc_actual)
    
    col1.metric("Saldo Disponible", f"{saldo_actual} OI")
    col2.metric("Social Credit", f"{sc_actual} SC")
    col3.metric("Sueldo Próximo", f"{sueldo_prev} OI")

    st.divider()

    # ENVIAR FONDOS
    st.subheader("💸 Enviar Fondos")
    destinatario = st.selectbox("Enviar a:", [n for n in st.session_state.usuarios.keys() if n != u_id])
    cantidad = st.number_input("Cantidad (OI)", min_value=1, max_value=int(saldo_actual) if saldo_actual > 0 else 1, step=1)
    if st.button("Confirmar Envío"):
        if st.session_state.usuarios[u_id]["saldo"] >= cantidad:
            st.session_state.usuarios[u_id]["saldo"] -= int(cantidad)
            st.session_state.usuarios[destinatario]["saldo"] += int(cantidad)
            st.success(f"Transferencia de {int(cantidad)} OI completada.")
            st.rerun()

    # --- HERRAMIENTAS DE GOBERNADOR (JUAN) ---
    if u_id == "Juan":
        st.divider()
        st.header("👑 Herramientas de Gobernador")
        accion = st.radio("Acción:", ["Pagar Sueldos", "Cobrar Impuestos", "Cambiar Social Credit"], horizontal=True)

        if accion == "Pagar Sueldos":
            st.write("Cada ciudadano recibirá su sueldo según la tabla oficial.")
            if st.button("EJECUTAR PAGO GLOBAL"):
                for n in st.session_state.usuarios:
                    pago = calcular_sueldo(st.session_state.usuarios[n]["sc"])
                    st.session_state.usuarios[n]["saldo"] += pago
                st.success("Sueldos pagados.")
                st.rerun()

        elif accion == "Cobrar Impuestos":
            sujeto_imp = st.selectbox("Cobrar a:", list(st.session_state.usuarios.keys()))
            monto_imp = st.number_input("Monto", min_value=1, value=1, step=1)
            if st.button(f"Cobrar a {sujeto_imp}"):
                st.session_state.usuarios[sujeto_imp]["saldo"] -= int(monto_imp)
                st.warning(f"Cobrados {monto_imp} OI.")
                st.rerun()

        elif accion == "Cambiar Social Credit":
            sujeto_sc = st.selectbox("Elegir ciudadano:", list(st.session_state.usuarios.keys()))
            sc_nuevo = st.slider("Nuevo SC", 0, 100, int(st.session_state.usuarios[sujeto_sc]["sc"]))
            if st.button(f"Actualizar SC"):
                st.session_state.usuarios[sujeto_sc]["sc"] = sc_nuevo
                st.success(f"SC de {sujeto_sc} actualizado.")
                st.rerun()
