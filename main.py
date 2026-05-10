import streamlit as st
import math

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="O.I.M.C. Banco Central", page_icon="🏛️", layout="wide")

# 2. INICIALIZACIÓN DE LA BASE DE DATOS (Se ejecuta al cargar la app)
if 'usuarios' not in st.session_state:
    st.session_state.usuarios = {
        "Juan": {"pin": "2325", "saldo": 10, "sc": 100, "rol": "admin"},
        "Asier": {"pin": "0084", "saldo": 10, "sc": 70, "rol": "user"},
        "Erika": {"pin": "0080", "saldo": 10, "sc": 70, "rol": "user"},
        "Nahia": {"pin": "0987", "saldo": 10, "sc": 70, "rol": "user"},
        "Gaizka": {"pin": "2100", "saldo": 10, "sc": 70, "rol": "user"},
        "Mikel": {"pin": "0870", "saldo": 10, "sc": 70, "rol": "user"},
        "Yolanda": {"pin": "2000", "saldo": 10, "sc": 70, "rol": "user"},
        "Jesús": {"pin": "0010", "saldo": 10, "sc": 70, "rol": "user"},
        "Iñaki": {"pin": "9999", "saldo": 10, "sc": 20, "rol": "user"}
    }

# Lógica de la tabla salarial de la foto
def calcular_sueldo(sc):
    if sc >= 90: return 5
    elif sc >= 70: return 4
    elif sc >= 50: return 2
    else: return 0

# 3. SISTEMA DE LOGIN
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

    # --- BARRA LATERAL (Izquierda) ---
    with st.sidebar:
        st.title(f"👤 {u_id}")
        if st.button("Cerrar Sesión"):
            del st.session_state.logeado
            st.rerun()
        
        st.divider()
        st.subheader("⚙️ Configuración")
        nuevo_pin = st.text_input("Nuevo PIN (4 dígitos)", type="password", max_chars=4)
        if st.button("Actualizar PIN"):
            st.session_state.usuarios[u_id]["pin"] = nuevo_pin
            st.success("PIN actualizado correctamente.")

    # --- CUERPO PRINCIPAL ---
    st.title("📊 Mi Cuenta Bancaria")
    
    # Métricas principales
    col1, col2, col3 = st.columns(3)
    saldo_actual = st.session_state.usuarios[u_id]["saldo"]
    sc_actual = st.session_state.usuarios[u_id]["sc"]
    sueldo_prev = calcular_sueldo(sc_actual)
    
    col1.metric("Saldo Disponible", f"{saldo_actual} OI")
    col2.metric("Social Credit", f"{sc_actual} SC")
    col3.metric("Sueldo Próximo", f"{sueldo_prev} OI")

    st.divider()

    # SECCIÓN ENVIAR FONDOS
    st.subheader("💸 Enviar Fondos")
    destinatario = st.selectbox("Enviar a:", [n for n in st.session_state.usuarios.keys() if n != u_id])
    max_posible = int(saldo_actual) if saldo_actual > 0 else 0
    cantidad = st.number_input("Cantidad de OI", min_value=1, max_value=max_posible if max_posible > 0 else 1, step=1)
    
    if st.button("Confirmar Envío"):
        if st.session_state.usuarios[u_id]["saldo"] >= cantidad:
            st.session_state.usuarios[u_id]["saldo"] -= int(cantidad)
            st.session_state.usuarios[destinatario]["saldo"] += int(cantidad)
            st.success(f"Has enviado {int(cantidad)} OI a {destinatario}.")
            st.rerun()
        else:
            st.error("Saldo insuficiente.")

    # --- PANEL EXCLUSIVO DE JUAN (ADMIN) ---
    if u_id == "Juan":
        st.divider()
        st.header("👑 Herramientas de Gobernador")
        
        opcion_admin = st.radio("Acción:", ["Pagar Sueldos", "Cobrar Impuestos", "Cambiar Social Credit"], horizontal=True)

        if opcion_admin == "Pagar Sueldos":
            st.subheader("💰 Pago Global de Nóminas")
            st.write("Se ingresará el sueldo automático a cada miembro según la tabla oficial.")
            if st.button("EJECUTAR PAGOS"):
                for nombre in st.session_state.usuarios:
                    pago = calcular_sueldo(st.session_state.usuarios[nombre]["sc"])
                    st.session_state.usuarios[nombre]["saldo"] += pago
                st.success("Sueldos pagados satisfactoriamente.")
                st.rerun()

        elif opcion_admin == "Cobrar Impuestos":
            st.subheader("⚖️ Recaudación para el Tesoro Real")
            # Solo deja elegir a otros que no sean Juan
            sujeto_imp = st.selectbox("Seleccionar ciudadano:", [n for n in st.session_state.usuarios.keys() if n != "Juan"])
            monto_imp = st.number_input("Monto de impuestos (OI)", min_value=1, value=1, step=1)
            
            if st.button(f"Cobrar a {sujeto_imp}"):
                # El dinero sale del ciudadano y va a Juan
                st.session_state.usuarios[sujeto_imp]["saldo"] -= int(monto_imp)
                st.session_state.usuarios["Juan"]["saldo"] += int(monto_imp)
                st.warning(f"Has recaudado {int(monto_imp)} OI de {sujeto_imp}.")
                st.rerun()

        elif opcion_admin == "Cambiar Social Credit":
            st.subheader("📈 Gestión de Estatus")
            sujeto_sc = st.selectbox("Elegir ciudadano:", list(st.session_state.usuarios.keys()))
            sc_nuevo = st.slider("Nuevo Social Credit", 0, 100, int(st.session_state.usuarios[sujeto_sc]["sc"]))
            if st.button(f"Actualizar SC de {sujeto_sc}"):
                st.session_state.usuarios[sujeto_sc]["sc"] = sc_nuevo
                st.success(f"Social Credit de {sujeto_sc} actualizado a {sc_nuevo}.")
                st.rerun()
