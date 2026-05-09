import streamlit as st

# Configuración
st.set_page_config(page_title="Banco O.I.M.C.", page_icon="🏦")

# --- BASE DE DATOS LIMPIA ---
if 'usuarios' not in st.session_state:
    st.session_state.usuarios = {
        "Iñaki": {"pin": "1010", "saldo": 0.0},
        "Asier": {"pin": "2020", "saldo": 0.0},
        "Juan": {"pin": "2025", "saldo": 0.0},
        "Amets": {"pin": "4040", "saldo": 0.0},
        "Erika": {"pin": "5050", "saldo": 0.0},
        "Nahia": {"pin": "6060", "saldo": 0.0},
        "Gaizka": {"pin": "7070", "saldo": 0.0},
        "Mikel": {"pin": "8080", "saldo": 0.0},
        "Yolanda": {"pin": "9090", "saldo": 0.0},
        "Jesús": {"pin": "0000", "saldo": 0.0}
    }

if 'sesion_activa' not in st.session_state:
    st.session_state.sesion_activa = None

# --- PANTALLA DE LOGIN ---
if st.session_state.sesion_activa is None:
    st.title("🏛️ Terminal Bancaria O.I.M.C.")
    user_input = st.text_input("Ingrese su Cuenta (Nombre):")
    pin_input = st.text_input("Ingrese su PIN:", type="password")
    
    if st.button("Acceder"):
        if user_input in st.session_state.usuarios:
            if pin_input == st.session_state.usuarios[user_input]["pin"]:
                st.session_state.sesion_activa = user_input
                st.rerun()
            else:
                st.error("❌ PIN incorrecto.")
        else:
            st.error("❌ Cuenta no encontrada.")

# --- PANEL DEL BANCO ---
else:
    usuario = st.session_state.sesion_activa
    st.title(f"💼 Panel de {usuario}")
    st.metric("Saldo Disponible", f"{st.session_state.usuarios[usuario]['saldo']} Oincalias")
    
    if st.button("Cerrar Sesión"):
        st.session_state.sesion_activa = None
        st.rerun()

    st.write("---")
    st.subheader("💸 Transferir Fondos")
    dest = st.text_input("Nombre del destinatario:")
    cant = st.number_input("Monto:", min_value=0.0, step=1.0)

    if st.button("Enviar"):
        if dest in st.session_state.usuarios and dest != usuario:
            if st.session_state.usuarios[usuario]["saldo"] >= cant and cant > 0:
                st.session_state.usuarios[usuario]["saldo"] -= cant
                st.session_state.usuarios[dest]["saldo"] += cant
                st.success("✅ Enviado.")
            else:
                st.error("Saldo insuficiente.")
        else:
            st.error("Usuario no válido.")

    if usuario == "Juan":
        st.write("---")
        st.subheader("👑 Panel Diplomático")
        t = st.selectbox("Inyectar a:", list(st.session_state.usuarios.keys()))
        m = st.number_input("Cantidad a crear:", min_value=0.0)
        if st.button("Inyectar"):
            st.session_state.usuarios[t]["saldo"] += m
            st.rerun()
