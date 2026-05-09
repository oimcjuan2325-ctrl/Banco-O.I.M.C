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
