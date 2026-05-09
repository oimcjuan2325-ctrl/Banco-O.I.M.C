import streamlit as st

# 1. CONFIGURACIÓN DE LA WEB
st.set_page_config(page_title="Banco Central O.I.M.C.", page_icon="🏛️")

# 2. BASE DE DATOS ESTRUCTURADA
if 'db' not in st.session_state:
    st.session_state.db = {
        "Juan":    {"pin": "3030", "saldo": 0.0, "sc": 100}, 
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

# 3. LÓGICA DE SUELDOS (Basado en el Social Credit del archivo e14ee7f5-3fc2-4d0d-90bc-d6e9bd65da43)
def obtener_datos_sc(sc):
    if sc >= 90: return "Elite", 5.0
    elif sc >= 70: return "Estándar", 4.0
    elif sc >= 50: return "Riesgo", 2.0
    else: return "Sancionado", 0.0

# 4. PANTALLA DE ACCESO
if st.session_state.usuario_identificado is None:
    st.title("🏛️ Terminal Bancaria O.I.M.C.")
    st.write("Ingrese su nombre y PIN para gestionar sus Oincalias.")
    with st.form("login"):
        u = st.text_input("Ciudadano:")
        p = st.text_input("PIN:", type="password")
        if st.form_submit_button("Entrar al Sistema"):
            if u in st.session_state.db and st.session_state.db[u]["pin"] == p:
                st.session_state.usuario_identificado = u
                st.rerun()
            else: st.error("❌ Error de autenticación.")

# 5. PANEL DE USUARIO
else:
    user = st.session_state.usuario_identificado
    datos = st.session_state.db[user]
    estatus, sueldo_v = obtener_datos_sc(datos["sc"])

    # Encabezado
    col_t, col_b = st.columns([3, 1])
    col_t.title(f"👤 Ciudadano: {user}")
    if col_b.button("Cerrar Sesión"):
        st.session_state.usuario_identificado = None
        st.rerun()

    st.write("---")
    
    # Visualización de Social Credit (Rojo si < 50)
    color_sc = "normal" if datos["sc"] >= 50 else "inverse"
    c1, c2, c3 = st.columns(3)
    c1.metric("Social Credit", f"{datos['sc']} pts", delta_color=color_sc)
    c2.metric("Estatus", estatus)
    c3.metric("Sueldo Semanal", f"{sueldo_v} OI")

    # Dinero Total (Rojo si es negativo)
    if datos["saldo"] < 0:
        st.markdown(f"### Dinero Total: :red[{datos['saldo']} OI] ⚠️")
        st.warning("Su cuenta está en números rojos. Debe impuestos a la Alianza.")
    else:
        st.subheader(f"Dinero Total: {datos['saldo']} OI")

    # 6. TRANSFERENCIAS
    st.write("---")
    st.subheader("💸 Enviar Oincalias")
    dest = st.selectbox("Seleccionar destino:", [n for n in st.session_state.db.keys() if n != user])
    monto = st.number_input("Cantidad a enviar:", min_value=0.0, step=0.5)
    if st.button("Confirmar Transferencia"):
        if datos["saldo"] >= monto and monto > 0:
            st.session_state.db[user]["saldo"] -= monto
            st.session_state.db[dest]["saldo"] += monto
            st.success(f"Has enviado {monto} OI a {dest}.")
            st.rerun()
        else: st.error("Saldo insuficiente o cantidad no válida.")

    # 7. GESTIÓN SUPREMA (SOLO JUAN)
    if user == "Juan":
        st.write("---")
        st.header("👑 Administración de la Alianza")
        
        # Ajustar Social Credit de otros
        target = st.selectbox("Gestionar Miembro:", list(st.session_state.db.keys()))
        n_sc = st.slider("Ajustar S.C.:", 0, 100, int(st.session_state.db[target]["sc"]))
        if st.button("Guardar Social Credit"):
            st.session_state.db[target]["sc"] = n_sc
            st.success(f"S.C. de {target} actualizado.")
            st.rerun()

        # --- SECCIÓN DE IMPUESTOS Y PAGO ---
        st.subheader("📊 Recaudación e Impuestos")
        impuesto = st.number_input("Impuesto semanal (OI):", min_value=0.0, value=1.0, step=0.1)
        
        if st.button("💸 EJECUTAR CICLO: PAGAR Y RECAUDAR"):
            total_recaudado = 0
            for m in st.session_state.db:
                # 1. Obtener sueldo por su S.C.
                _, monto_pago = obtener_datos_sc(st.session_state.db[m]["sc"])
                
                # 2. Si el miembro NO es Juan, le quitamos el impuesto
                if m != "Juan":
                    st.session_state.db[m]["saldo"] += (monto_pago - impuesto)
                    total_recaudado += impuesto
                else:
                    # Juan solo cobra su sueldo (no se paga impuesto a sí mismo)
                    st.session_state.db[m]["saldo"] += monto_pago
            
            # 3. El dinero recaudado va a la cuenta de Juan
            st.session_state.db["Juan"]["saldo"] += total_recaudado
            st.balloons()
            st.success(f"¡Ciclo completado! Has recaudado {total_recaudado} OI para el Tesoro.")
            st.rerun()
