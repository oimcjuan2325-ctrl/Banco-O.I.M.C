import streamlit as st

# Configuración
st.set_page_config(page_title="Banco O.I.M.C. - Sistema S.C.", page_icon="🏛️")

# --- BASE DE DATOS CON SOCIAL CREDIT ---
if 'usuarios' not in st.session_state:
    miembros = ["Iñaki", "Asier", "Juan", "Amets", "Erika", "Naya", "Gaizka", "Mikel", "Holanda", "Jesús"]
    # Todos empiezan con 0 Oincalias y 70 de Social Credit (Estándar)
    st.session_state.usuarios = {m: {"pin": "0000", "saldo": 0.0, "sc": 70} for m in miembros}
    st.session_state.usuarios["Juan"]["pin"] = "3030" # Tu PIN

if 'sesion_activa' not in st.session_state:
    st.session_state.sesion_activa = None

# Función para calcular sueldo según S.C. (Basado en tu tabla)
def calcular_sueldo(sc):
    if sc >= 90: return 5.0  # Elite
    if sc >= 70: return 4.0  # Estándar
    if sc >= 50: return 2.0  # Riesgo
    return 0.0              # Sancionado

# --- LOGIN ---
if st.session_state.sesion_activa is None:
    st.title("🏛️ Terminal O.I.M.C.")
    u_in = st.text_input("Cuenta:")
    p_in = st.text_input("PIN:", type="password")
    if st.button("Acceder"):
        if u_in in st.session_state.usuarios and p_in == st.session_state.usuarios[u_in]["pin"]:
            st.session_state.sesion_activa = u_in
            st.rerun()
        else:
            st.error("Credenciales incorrectas")

# --- INTERFAZ BANCARIA ---
else:
    user = st.session_state.sesion_activa
    datos = st.session_state.usuarios[user]
    
    st.title(f"💼 Ciudadano: {user}")
    
    # Mostrar Social Credit y Sueldo Correspondiente
    col1, col2, col3 = st.columns(3)
    col1.metric("Social Credit", f"{datos['sc']} pts")
    
    sueldo_prox = calcular_sueldo(datos['sc'])
    status = "Elite" if datos['sc']>=90 else "Estándar" if datos['sc']>=70 else "Riesgo" if datos['sc']>=50 else "Sancionado"
    
    col2.metric("Estatus", status)
    col3.metric("Sueldo Semanal", f"{sueldo_prox} OI")

    st.write(f"💰 **Saldo en cuenta:** {datos['saldo']} Oincalias")

    if st.button("Cerrar Sesión"):
        st.session_state.sesion_activa = None
        st.rerun()

    st.write("---")
    # --- TRANSFERENCIAS ---
    st.subheader("💸 Transferencia Digital")
    dest = st.text_input("Enviar a:")
    monto = st.number_input("Monto:", min_value=0.0)
    if st.button("Confirmar Envío"):
        if dest in st.session_state.usuarios and datos['saldo'] >= monto:
            st.session_state.usuarios[user]['saldo'] -= monto
            st.session_state.usuarios[dest]['saldo'] += monto
            st.success("Transferencia realizada")
            st.rerun()

    # --- PANEL DIPLOMÁTICO (SOLO JUAN) ---
    if user == "Juan":
        st.write("---")
        st.subheader("👑 Gestión de la Alianza")
        
        target = st.selectbox("Miembro:", list(st.session_state.usuarios.keys()))
        nuevo_sc = st.slider("Ajustar Social Credit:", 0, 100, int(st.session_state.usuarios[target]['sc']))
        
        if st.button("Actualizar S.C."):
            st.session_state.usuarios[target]['sc'] = nuevo_sc
            st.success(f"Social Credit de {target} actualizado a {nuevo_sc}")
            st.rerun()
            
        if st.button("💸 PAGAR TODOS LOS SUELDOS (VIERNES)"):
            for m in st.session_state.usuarios:
                pago = calcular_sueldo(st.session_state.usuarios[m]['sc'])
                st.session_state.usuarios[m]['saldo'] += pago
            st.balloons()
            st.success("Se han ingresado los sueldos según el Social Credit de cada uno.")
