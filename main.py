import streamlit as st

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Banco O.I.M.C.", page_icon="🏛️")

# 2. BASE DE DATOS INICIAL
if 'db' not in st.session_state:
    st.session_state.db = {
        "Juan":    {"pin": "3030", "saldo": 0, "sc": 100}, 
        "Iñaki":   {"pin": "1010", "saldo": 0, "sc": 20},
        "Asier":   {"pin": "2020", "saldo": 0, "sc": 70},
        "Amets":   {"pin": "4040", "saldo": 0, "sc": 70},
        "Erika":   {"pin": "5050", "saldo": 0, "sc": 70},
        "Nahia":   {"pin": "6060", "saldo": 0, "sc": 70},
        "Gaizka":  {"pin": "7070", "saldo": 0, "sc": 70},
        "Mikel":   {"pin": "8080", "saldo": 0, "sc": 70},
        "Yolanda": {"pin": "9090", "saldo": 0, "sc": 70},
        "Jesús":   {"pin": "0000", "saldo": 0, "sc": 70}
    }

if 'usuario_identificado' not in st.session_state:
    st.session_state.usuario_identificado = None

# 3. LÓGICA DE SUELDOS (ENTEROS)
def obtener_datos_sc(sc):
    if sc >= 90: return "Elite", 5
    elif sc >= 70: return "Estándar", 4
    elif sc >= 50: return "Riesgo", 2
    else: return "Sancionado", 0

# 4. LOGIN
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

# 5. PANEL DE USUARIO
else:
    user = st.session_state.usuario_identificado
    datos = st.session_state.db[user]
    estatus, sueldo_v = obtener_datos_sc(datos["sc"])

    col_t, col_b = st.columns([3, 1])
    col_t.title(f"👤 {user}")
    if col_b.button("Salir"):
        st.session_state.usuario_identificado = None
        st.rerun()

    st.write("---")
    
    # Visualización
    c1, c2, c3 = st.columns(3)
    c1.metric("Social Credit", f"{datos['sc']} pts", delta_color="normal" if datos["sc"] >= 50 else "inverse")
    c2.metric("Estatus", estatus)
    c3.metric("Sueldo Semanal", f"{sueldo_v} OI")

    if datos["saldo"] < 0:
        st.markdown(f"### Dinero Total: :red[{datos['saldo']} OI] ⚠️")
    else:
        st.subheader(f"Dinero Total: {datos['saldo']} OI")

    # 6. TRANSFERENCIAS (CON REFRESO)
    st.write("---")
    st.subheader("💸 Enviar Oincalias")
    dest = st.selectbox("Enviar a:", [n for n in st.session_state.db.keys() if n != user])
    monto_envio = st.number_input("Cantidad:", min_value=0, step=1)
    if st.button("Confirmar Envío"):
        if datos["saldo"] >= monto_envio and monto_envio > 0:
            st.session_state.db[user]["saldo"] -= int(monto_envio)
            st.session_state.db[dest]["saldo"] += int(monto_envio)
            st.success(f"✅ ¡Enviadas {monto_envio} OI!")
            st.rerun() # Esto hace que el saldo cambie visualmente al momento
        else:
            st.error("No tienes saldo suficiente.")

    # 7. ADMINISTRACIÓN (JUAN)
    if user == "Juan":
        st.write("---")
        st.header("👑 Administración Suprema")
        target = st.selectbox("Miembro:", list(st.session_state.db.keys()))
        
        n_sc = st.slider("Ajustar S.C.:", 0, 100, int(st.session_state.db[target]["sc"]))
        if st.button("Guardar S.C."):
            st.session_state.db[target]["sc"] = n_sc
            st.rerun()

        st.subheader("📊 Nóminas e Impuestos")
        imp_fijo = st.number_input("Impuesto hoy (OI):", min_value=0, value=0, step=1)
        
        if st.button("💸 EJECUTAR CICLO"):
            total_imp = 0
            for m in st.session_state.db:
                _, pago = obtener_datos_sc(st.session_state.db[m]["sc"])
                if m != "Juan":
                    st.session_state.db[m]["saldo"] += (pago - imp_fijo)
                    total_imp += imp_fijo
                else:
                    st.session_state.db[m]["saldo"] += pago
            
            st.session_state.db["Juan"]["saldo"] += total_imp
            st.balloons()
            st.rerun()
