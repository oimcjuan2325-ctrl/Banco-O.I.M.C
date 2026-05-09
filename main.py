import streamlit as st

# Configuración de la página
st.set_page_config(page_title="Banco O.I.M.C.", page_icon="🏦")

st.title("🏦 Sistema Bancario O.I.M.C.")
st.write("---")

# Base de datos simplificada
if 'banco' not in st.session_state:
    st.session_state.banco = {
        "Iñaki": 0000
        "Asier": 0000
        "Juan": 0000
        "Amets": 0000
        "Erika": 0000
        "Nahia": 0000
        "Gaizka": 0000
        "MIkel": 0000
        "Yolanda": 0000
        "Jesús": 0000
    }

# Panel Lateral
st.sidebar.header("Acceso Ciudadano")
user = st.sidebar.selectbox("Identificarse como:", list(st.session_state.banco.keys()))
st.sidebar.metric("Saldo Actual", f"{st.session_state.banco[user]} OI")

# Formulario de Envío
st.subheader("💸 Realizar Transferencia")
destinatario = st.selectbox("Enviar a:", [u for u in st.session_state.banco.keys() if u != user])
cantidad = st.number_input("Monto a enviar:", min_value=0.0, step=1.0)

if st.button("Confirmar Transacción"):
    if st.session_state.banco[user] >= cantidad:
        st.session_state.banco[user] -= cantidad
        st.session_state.banco[destinatario] += cantidad
        st.success(f"¡Éxito! Has enviado {cantidad}€ a {destinatario}")
    else:
        st.error("Fondos insuficientes en tu cuenta.")
            import streamlit as st

# Configuración estética de la banca
st.set_page_config(page_title="Banca Privada O.I.M.C.", page_icon="🏛️")

# --- BASE DE DATOS SECRETA (Solo tú la ves aquí en el código) ---
if 'usuarios' not in st.session_state:
    # Todos empiezan con 0 Oincalias
    st.session_state.usuarios = {
        "Iñaki": {"pin": "1010", "saldo": 0.0},
        "Asier": {"pin": "2020", "saldo": 0.0},
        "Juan": {"pin": "3030", "saldo": 0.0},
        "Amets": {"pin": "4040", "saldo": 0.0},
        "Erika": {"pin": "5050", "saldo": 0.0},
        "Naya": {"pin": "6060", "saldo": 0.0},
        "Gaizka": {"pin": "7070", "saldo": 0.0},
        "Mikel": {"pin": "8080", "saldo": 0.0},
        "Yolanda": {"pin": "9090", "saldo": 0.0},
        "Jesús": {"pin": "0000", "saldo": 0.0}
    }

if 'sesion_activa' not in st.session_state:
    st.session_state.sesion_activa = None

# --- PANTALLA DE ACCESO (LOGIN) ---
if st.session_state.sesion_activa is None:
    st.title("🏛️ Terminal Bancaria O.I.M.C.")
    st.markdown("### Por favor, identifíquese para continuar")
    
    # El usuario debe escribir su nombre y su PIN
    user_input = st.text_input("Ingrese su Cuenta (Nombre):")
    pin_input = st.text_input("Ingrese su PIN de seguridad:", type="password")
    
    if st.button("Acceder a mi Cuenta"):
        if user_input in st.session_state.usuarios:
            if pin_input == st.session_state.usuarios[user_input]["pin"]:
                st.session_state.sesion_activa = user_input
                st.rerun()
            else:
                st.error("❌ PIN incorrecto. Inténtelo de nuevo.")
        else:
            st.error("❌ La cuenta ingresada no existe en los registros de la Alianza.")

# --- INTERFAZ DEL BANCO (DENTRO DE LA CUENTA) ---
else:
    usuario = st.session_state.sesion_activa
    st.title(f"💼 Panel de Control: {usuario}")
    
    # Mostrar Saldo en grande
    saldo_actual = st.session_state.usuarios[usuario]["saldo"]
    st.metric("Saldo Disponible", f"{saldo_actual} Oincalias")
    
    if st.button("Cerrar Sesión"):
        st.session_state.sesion_activa = None
        st.rerun()

    st.write("---")

    # --- SISTEMA DE TRANSFERENCIAS ---
    st.subheader("💸 Transferir Fondos")
    destinatario = st.text_input("Nombre del destinatario (exacto):")
    cantidad = st.number_input("Monto en Oincalias:", min_value=0.0, step=0.5)

    if st.button("Ejecutar Transferencia"):
        if destinatario in st.session_state.usuarios and destinatario != usuario:
            if st.session_state.usuarios[usuario]["saldo"] >= cantidad and cantidad > 0:
                # Proceso de envío
                st.session_state.usuarios[usuario]["saldo"] -= cantidad
                st.session_state.usuarios[destinatario]["saldo"] += cantidad
                st.success(f"✅ Transferencia de {cantidad} Oincalias enviada a {destinatario}.")
            else:
                st.error("Fondos insuficientes para esta operación.")
        else:
            st.error("Destinatario no válido o nombre mal escrito.")

    # --- PODER DEL DIPLOMÁTICO (Solo Juan) ---
    if usuario == "Juan":
        st.write("---")
        st.subheader("👑 Autoridad Central")
        target = st.selectbox("Emitir moneda para:", list(st.session_state.usuarios.keys()))
        monto_crear = st.number_input("Cantidad a inyectar:", min_value=0.0)
        if st.button("Inyectar Oincalias"):
            st.session_state.usuarios[target]["saldo"] += monto_crear
            st.success(f"Se han añadido {monto_crear} Oincalias a la cuenta de {target}")
            st.rerun()
