import streamlit as st

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Banco O.I.M.C. Oficial", page_icon="🏦")

# 2. BASE DE DATOS ESTRUCTURADA
if 'db' not in st.session_state:
    st.session_state.db = {
        "Juan":    {"pin": "3030", "saldo": 0.0, "sc": 70}, 
        "Iñaki":   {"pin": "1010", "saldo": 0.0, "sc": 70},
        "Asier":   {"pin": "2020", "saldo": 0.0, "sc": 70},
        "Amets":   {"pin": "4040", "saldo": 0.0, "sc": 70},
        "Erika":   {"pin": "5050", "saldo": 0.0, "sc": 70},
        "Nahia":   {"pin": "6060", "saldo": 0.0, "sc": 70},
        "Gaizka":  {"pin": "7070", "saldo": 0.0, "sc": 70},
        "Mikel":   {"pin": "8080", "saldo": 0.0, "sc": 70},
        "Yolanda": {"pin": "9090", "saldo": 0.0, "sc": 70},
        "Jesús":   {"pin": "0000", "saldo": 0.0, "sc": 70}
    }

if 'usuario_identificado' not in st.session_state:
    st.session_state.usuario_identificado = None

# Lógica de Sueldos
def obtener_info_sueldo(sc):
    if sc >= 90: return "Elite", 5.0, "normal"
    elif sc >= 70: return "Estándar", 4.0, "normal"
    elif sc >= 50: return "Riesgo", 2.0, "normal"
    else: return "Sancionado", 0.0, "inverse"

# 3. PANTALLA DE ACCESO
if st.session_state.usuario_identificado is None:
    st.title("🏛️ Terminal O.I.M.C.")
    with st.form("login"):
        u = st.text_input("Usuario:")
        p = st.text_input("PIN:", type="password")
        if st.form_submit_button("Entrar"):
            if u in st.session_state.db and st.session_state.db[u]["pin"] == p:
                st.session_state.usuario_identificado = u
                st.rerun()
            else: st.error("Acceso denegado.")

# 4. PANEL DE USUARIO CON DETALLES VISUALES
else:
    user = st.session_state.usuario_identificado
    datos = st.session_state.db[user]
    estatus, sueldo, modo = obtener_info_sueldo(datos["sc"])

    col_t, col_b = st.columns([3, 1])
    col_t.title(f"👤 Ciudadano: {user}")
    if col_b.button("Salir"):
        st.session_state.usuario_identificado = None
        st.rerun()

    st.write("---")

    # --- LÓGICA DE COLORES ---
    # Color del Social Credit
    color_sc = "normal" if datos["sc"] >= 50 else "inverse"
    
    # Color del Saldo
    color_saldo = "normal" if datos["saldo"] >= 0 else "inverse"

    c1, c2, c3 = st.columns(3)
    c1.metric("Social Credit", f"{datos['sc']} pts", delta_color=color_sc)
    c2.metric("Estatus", estatus)
    c3.metric("Sueldo Semanal", f"{sueldo} OI")

    # DINERO TOTAL CON ALERTA SI ES NEGATIVO
    if datos["saldo"] < 0:
        st.markdown(f"### Dinero Total: :red[{datos['saldo']} OI] ⚠️")
        st.error("Usted tiene una deuda con la Alianza.")
    else:
        st.subheader(f"Dinero Total: {datos['saldo']} OI")

    # Alerta visual si el Social Credit es bajo
    if datos["sc"] < 50:
        st.warning("🚨 ADVERTENCIA: Su Social Credit es demasiado bajo. Está bajo vigilancia.")

    st.write("---")
    # TRANSFERENCIAS
    st.subheader("💸 Transferencia Digital")
    dest = st.selectbox("Destinatario:", [n for n in st.session_state.db.keys() if n != user])
    cant = st.number_input("Cantidad:", min_value=0.0, step=1.0)
    if st.button("Enviar OI"):
        if datos["saldo"] >= cant and cant > 0:
            st.session_state.db[user]["saldo"] -= cant
            st.session_state.db[dest]["saldo"] += cant
            st.success("Transacción completada.")
            st.rerun()
        else:
            st.error("Fondos insuficientes.")

    # 5. PANEL DE CONTROL (SOLO JUAN)
    if user == "Juan":
        st.write("---")
        st.header("👑 Administración Suprema")
        target = st.selectbox("Miembro a gestionar:", list(st.session_state.db.keys()))
        
        # Ajuste de SC
        n_sc = st.slider("Ajustar Social Credit:", 0, 100, int(st.session_state.db[target]["sc"]))
        if st.button("Guardar S.C."):
            st.session_state.db[target]["sc"] = n_sc
            st.rerun()
            
        # Ajuste de Saldo Manual (Para multas o bonus)
        n_saldo = st.number_input("Añadir/Quitar Saldo (usa '-' para quitar):", value=0.0)
        if st.button("Modificar Saldo"):
            st.session_state.db[target]["saldo"] += n_saldo
            st.success(f"Saldo de {target} modificado.")
            st.rerun()

        if st.button("💸 PAGAR NÓMINAS (VIERNES)"):
            for m in st.session_state.db:
                _, pago, _ = obtener_info_sueldo(st.session_state.db[m]["sc"])
                st.session_state.db[m]["saldo"] += pago
            st.balloons()
