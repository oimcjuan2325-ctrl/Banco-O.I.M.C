import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Banco Central O.I.M.C.", page_icon="🏛️")

# 2. BASE DE DATOS (Aquí cambias tú los saldos iniciales cada semana)
if 'db' not in st.session_state:
    st.session_state.db = {
        "Juan":    {"pin": "3030", "saldo": 10, "sc": 100}, 
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

# 3. LÓGICA
def obtener_datos_sc(sc):
    if sc >= 90: return "Elite", 5
    elif sc >= 70: return "Estándar", 4
    elif sc >= 50: return "Riesgo", 2
    else: return "Sancionado", 0

# 4. INTERFAZ
if st.session_state.usuario_identificado is None:
    st.title("🏛️ Terminal O.I.M.C.")
    with st.form("login"):
        u = st.text_input("Usuario")
        p = st.text_input("PIN", type="password")
        if st.form_submit_button("Entrar"):
            if u in st.session_state.db and st.session_state.db[u]["pin"] == p:
                st.session_state.usuario_identificado = u
                st.rerun()
            else: st.error("Acceso denegado")
else:
    user = st.session_state.usuario_identificado
    datos = st.session_state.db[user]
    estatus, sueldo = obtener_datos_sc(datos["sc"])

    st.title(f"👤 {user}")
    st.metric("Saldo Actual", f"{datos['saldo']} OI")
    st.write(f"Estatus: **{estatus}** | Sueldo: **{sueldo} OI**")

    # TRANSFERENCIAS
    st.write("---")
    dest = st.selectbox("Enviar a:", [n for n in st.session_state.db.keys() if n != user])
    monto = st.number_input("Cantidad:", min_value=0, step=1)
    if st.button("Confirmar Envío"):
        if datos["saldo"] >= monto and monto > 0:
            st.session_state.db[user]["saldo"] -= int(monto)
            st.session_state.db[dest]["saldo"] += int(monto)
            st.success("Transacción completada")
            st.rerun()

    if st.button("Cerrar Sesión"):
        st.session_state.usuario_identificado = None
        st.rerun()

    # 5. PANEL DE JUAN (PARA GUARDAR DATOS)
    if user == "Juan":
        st.write("---")
        st.header("👑 Administración")
        
        # Botón para pagar a todos
        if st.button("💸 PAGAR NÓMINAS"):
            for m in st.session_state.db:
                _, pago = obtener_datos_sc(st.session_state.db[m]["sc"])
                st.session_state.db[m]["saldo"] += pago
            st.balloons()
            st.rerun()

        # Generador de reporte para tu Excel
        st.subheader("💾 Guardar Progreso")
        if st.button("Generar Reporte"):
            resumen = [{"Nombre": k, "Saldo": v["saldo"]} for k, v in st.session_state.db.items()]
            st.table(pd.DataFrame(resumen))
            st.info("Juan, anota estos números en tu Excel antes de cerrar la web.")
