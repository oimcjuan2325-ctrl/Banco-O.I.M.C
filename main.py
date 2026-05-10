import streamlit as st

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="O.I.M.C. Central Bank", page_icon="🏛️")

# 2. BASE DE DATOS DE LA ALIANZA
# Nota: En Streamlit Cloud, para que los datos no se borren al cerrar, 
# lo ideal es conectar un Google Sheets. Por ahora, esto funciona en la sesión.
if 'usuarios' not in st.session_state:
    st.session_state.usuarios = {
        "Juan": {"pin": "1234", "saldo": 10.0, "sc": 100, "rol": "admin"},
        "Asier": {"pin": "2020", "saldo": 10.0, "sc": 80, "rol": "user"},
        "Erika": {"pin": "0000", "saldo": 10.0, "sc": 80, "rol": "user"},
        "Nahia": {"pin": "0231", "saldo": 10.0, "sc": 80, "rol": "user"},
        "Gaizka": {"pin": "2310", "saldo": 10.0, "sc": 80, "rol": "user"},
        "Mikel": {"pin": "0000", "saldo": 10.0, "sc": 80, "rol": "user"},
        "Yolanda": {"pin": "0000", "saldo": 10.0, "sc": 80, "rol": "user"},
        "Jesús": {"pin": "0000", "saldo": 10.0, "sc": 80, "rol": "user"},
        "Iñaki": {"pin": "9999", "saldo": 10.0, "sc": 10, "rol": "user"}
    }

# 3. SISTEMA DE LOGIN
if 'usuario_logeado' not in st.session_state:
    st.title("🏛️ O.I.M.C. - Acceso Central")
    st.write("Bienvenido al sistema financiero de la Alianza.")
    user = st.selectbox("Selecciona tu nombre", list(st.session_state.usuarios.keys()))
    pin = st.text_input("Introduce tu PIN de 4 dígitos", type="password")
    
    if st.button("Entrar al Sistema"):
        if st.session_state.usuarios[user]["pin"] == pin:
            st.session_state.usuario_logeado = user
            st.success(f"Sesión iniciada como {user}")
            st.rerun()
        else:
            st.error("PIN incorrecto. Contacta con el Gobernador Juan.")
else:
    # --- INTERFAZ DE USUARIO LOGEADO ---
    user_actual = st.session_state.usuario_logeado
    datos = st.session_state.usuarios[user_actual]
    
    st.sidebar.title(f"👤 {user_actual}")
    st.sidebar.write(f"Estatus: {datos['rol'].upper()}")
    
    if st.sidebar.button("Cerrar Sesión"):
        del st.session_state.usuario_logeado
        st.rerun()

    # CAMBIO DE PIN
    with st.sidebar.expander("⚙️ Seguridad"):
        nuevo_pin = st.text_input("Cambiar PIN (4 dígitos)", max_chars=4)
        if st.button("Actualizar PIN"):
            st.session_state.usuarios[user_actual]["pin"] = nuevo_pin
            st.success("PIN actualizado correctamente")

    # PANEL DE SALDOS
    st.title("📊 Mi Cuenta Bancaria")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Saldo Disponible", f"{st.session_state.usuarios[user_actual]['saldo']} OI")
    col2.metric("Social Credit", f"{datos['sc']} SC")
    
    # Sueldo automático basado en Social Credit
    sueldo_semanal = datos['sc'] / 10
    col3.metric("Sueldo Próximo", f"{sueldo_semanal} OI")

    st.divider()

    # --- TRANSFERENCIAS AUTOMÁTICAS ---
    st.subheader("💸 Enviar Fondos")
    destinatario = st.selectbox("Enviar a:", [u for u in st.session_state.usuarios.keys() if u != user_actual])
    cantidad = st.number_input("Cantidad de Oincalias", min_value=0.1, max_value=float(st.session_state.usuarios[user_actual]['saldo']), step=1.0)
    
    if st.button("Confirmar Transferencia"):
        # EJECUCIÓN AUTOMÁTICA (SUMA Y RESTA)
        st.session_state.usuarios[user_actual]["saldo"] -= cantidad
        st.session_state.usuarios[destinatario]["saldo"] += cantidad
        st.success(f"Has enviado {cantidad} OI a {destinatario} correctamente.")
        st.balloons()
        st.rerun()

    # --- PANEL EXCLUSIVO DE JUAN (ADMIN) ---
    if datos['rol'] == "admin":
        st.divider()
        st.header("👑 Herramientas de Gobernador")
        
        accion = st.radio("Operación Bancaria:", ["Pagar Sueldos (Global)", "Cobrar Impuestos (Individual)"])
        
        if accion == "Pagar Sueldos (Global)":
            st.write("Este botón pagará a cada ciudadano su sueldo basado en su Social Credit actual.")
            if st.button("EJECUTAR PAGO DE NÓMINAS"):
                for u in st.session_state.usuarios:
                    pago = st.session_state.usuarios[u]["sc"] / 10
                    st.session_state.usuarios[u]["saldo"] += pago
                st.success("Nóminas procesadas. Los saldos han sido actualizados.")
                st.rerun()
        
        elif accion == "Cobrar Impuestos (Individual)":
            sujeto = st.selectbox("Seleccionar ciudadano:", list(st.session_state.usuarios.keys()))
            # El sistema sugiere 2 OI para Iñaki y 1 OI para el resto
            sugerencia = 2.0 if sujeto == "Iñaki" else 1.0
            monto = st.number_input("Monto a retirar:", value=sugerencia)
            
            if st.button(f"Ejecutar Cobro a {sujeto}"):
                st.session_state.usuarios[sujeto]["saldo"] -= monto
                st.warning(f"Se han detraído {monto} OI de la cuenta de {sujeto}")
                st.rerun()
