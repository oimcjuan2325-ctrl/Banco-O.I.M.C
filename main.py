import streamlit as st
import math

# 1. CONFIGURACIÓN
st.set_page_config(page_title="O.I.M.C. Central Bank", page_icon="🏛️")

# 2. BASE DE DATOS SIN CÉNTIMOS
if 'usuarios' not in st.session_state:
    st.session_state.usuarios = {
        "Juan": {"pin": "2325", "saldo": 10, "sc": 100, "rol": "admin"},
        "Asier": {"pin": "2020", "saldo": 10, "sc": 80, "rol": "user"},
        "Erika": {"pin": "2013", "saldo": 10, "sc": 80, "rol": "user"},
        "Nahia": {"pin": "9389", "saldo": 10, "sc": 80, "rol": "user"},
        "Gaizka": {"pin": "2932", "saldo": 10, "sc": 80, "rol": "user"},
        "Mikel": {"pin": "2048", "saldo": 10, "sc": 80, "rol": "user"},
        "Yolanda": {"pin": "1977", "saldo": 10, "sc": 80, "rol": "user"},
        "Jesús": {"pin": "0000", "saldo": 10, "sc": 80, "rol": "user"},
        "Iñaki": {"pin": "9999", "saldo": 10, "sc": 10, "rol": "user"}
    }

# 3. LOGIN
if 'usuario_logeado' not in st.session_state:
    st.title("🏛️ O.I.M.C. - Acceso Central")
    user = st.selectbox("Selecciona tu nombre", list(st.session_state.usuarios.keys()))
    pin = st.text_input("PIN de 4 dígitos", type="password")
    
    if st.button("Entrar"):
        if st.session_state.usuarios[user]["pin"] == pin:
            st.session_state.usuario_logeado = user
            st.rerun()
        else:
            st.error("PIN incorrecto")
else:
    user_actual = st.session_state.usuario_logeado
    datos = st.session_state.usuarios[user_actual]
    
    st.sidebar.title(f"👤 {user_actual}")
    if st.sidebar.button("Cerrar Sesión"):
        del st.session_state.usuario_logeado
        st.rerun()

    # PANEL BANCARIO
    st.title("📊 Mi Cuenta Bancaria")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Saldo Disponible", f"{int(st.session_state.usuarios[user_actual]['saldo'])} OI")
    col2.metric("Social Credit", f"{int(datos['sc'])} SC")
    
    # SUELDO REDONDEADO (Cobra 1 OI por cada 10 de SC)
    sueldo_semanal = math.ceil(datos['sc'] / 10) 
    col3.metric("Sueldo Próximo", f"{int(sueldo_semanal)} OI")

    st.divider()

    # TRANSFERENCIAS (SOLO ENTEROS)
    st.subheader("💸 Enviar Fondos")
    destinatario = st.selectbox("Enviar a:", [u for u in st.session_state.usuarios.keys() if u != user_actual])
    cantidad = st.number_input("Cantidad (Solo números enteros)", min_value=1, max_value=int(st.session_state.usuarios[user_actual]['saldo']), step=1)
    
    if st.button("Confirmar Envío"):
        st.session_state.usuarios[user_actual]["saldo"] -= int(cantidad)
        st.session_state.usuarios[destinatario]["saldo"] += int(cantidad)
        st.success(f"Transferencia de {int(cantidad)} OI completada.")
        st.rerun()

    # PANEL DE JUAN (ADMIN)
    if datos['rol'] == "admin":
        st.divider()
        st.header("👑 Herramientas de Gobernador")
        
        opcion = st.radio("Acción:", ["Sueldos", "Impuestos"])
        
        if opcion == "Sueldos":
            if st.button("PAGAR NÓMINAS REDONDAS"):
                for u in st.session_state.usuarios:
                    pago = math.ceil(st.session_state.usuarios[u]["sc"] / 10)
                    st.session_state.usuarios[u]["saldo"] += pago
                st.success("Sueldos pagados sin céntimos.")
                st.rerun()
        
        elif opcion == "Impuestos":
            sujeto = st.selectbox("Cobrar a:", list(st.session_state.usuarios.keys()))
            monto = st.number_input("Monto impuesto", value=2 if sujeto == "Iñaki" else 1, step=1)
            if st.button(f"Cobrar a {sujeto}"):
                st.session_state.usuarios[sujeto]["saldo"] -= int(monto)
                st.warning(f"Cobrados {int(monto)} OI")
                st.rerun()
