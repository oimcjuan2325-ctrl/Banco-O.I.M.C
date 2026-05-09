import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Banco Central O.I.M.C.", page_icon="🏛️")

# 2. BASE DE DATOS INICIAL (Todos empiezan con 10 OI)
if 'db' not in st.session_state:
    st.session_state.db = {
        "Juan":    {"pin": "3030", "saldo": 10, "sc": 100}, 
        "Iñaki":   {"pin": "1010", "saldo": 10, "sc": 20},
        "Asier":   {"pin": "2020", "saldo": 10, "sc": 70},
        "Amets":   {"pin": "4040", "saldo": 10, "sc": 70},
        "Erika":   {"pin": "5050", "saldo": 10, "sc": 70},
        "Nahia":   {"pin": "6060", "saldo": 10, "sc": 70},
        "Gaizka":  {"pin": "7070", "saldo": 10, "sc": 70},
        "Mikel":   {"pin": "8080", "saldo": 10, "sc": 70},
        "Yolanda": {"pin": "9090", "saldo": 10, "sc": 70},
        "Jesús":   {"pin": "0000", "saldo": 10, "sc": 70}
    }

if 'usuario_identificado' not in st.session_state:
    st.session_state.usuario_identificado = None

# 3. LÓGICA DE ESTATUS
def obtener_datos_sc(sc):
    if sc >= 90: return "Elite", 5
    elif sc >= 70: return "Estándar", 4
    elif sc >= 50: return "Riesgo", 2
    else: return "Sancionado", 0

# 4. LOGIN
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

# 5. PANEL DE USUARIO
else:
    user = st.session_state.usuario_identificado
    datos = st.session_state.db[user]
    estatus, sueldo_v = obtener_datos_sc(datos["sc"])

    col1, col2 = st.columns([3, 1])
    col1.title(f"👤 {user}")
    if col2.button("Cerrar Sesión"):
        st.session_state.usuario_identificado = None
        st.rerun()

    st.write("---")
    c1, c2, c3 = st.columns(3)
    c1.metric("Social Credit", f"{datos['sc']} pts")
    c2.metric("Estatus", estatus)
    c3.metric("Sueldo Semanal", f"{sueldo_v} OI")

    if datos["saldo"] < 0:
        st.markdown(f"### Dinero Total: :red[{datos['saldo']} OI] ⚠️")
    else:
        st.subheader(f"Dinero Total: {datos['saldo']} OI")

    # 6. TRANSFERENCIAS
    st.write("---")
    st.subheader("💸 Enviar Oincalias")
    dest = st.selectbox("Enviar a:", [n for n in st.session_state.db.keys() if n != user])
    monto_envio = st.number_input("Cantidad:", min_value=0, step=1)
    if st.button("Confirmar Envío"):
        if datos["saldo"] >= monto_envio and monto_envio > 0:
            st.session_state.db[user]["saldo"] -= int(monto_envio)
            st.session_state.db[dest]["saldo"] += int(monto_envio)
            st.success(f"✅ ¡Enviadas {monto_envio} OI a {dest}!")
            st.rerun()
        else:
            st.error("Saldo insuficiente o cantidad inválida.")

    # 7. ADMINISTRACIÓN SUPREMA (Solo Juan)
    if user == "Juan":
        st.write("---")
        st.header("👑 Panel de Control Supremo")
        
        # Editar Social Credit
        target = st.selectbox("Gestionar Miembro:", list(st.session_state.db.keys()))
        nuevo_sc = st.slider("Ajustar Social Credit:", 0, 100, int(st.session_state.db[target]["sc"]))
        if st.button("Actualizar S.C."):
            st.session_state.db[target]["sc"] = nuevo_sc
            st.success(f"S.C. de {target} actualizado.")
            st.rerun()

        # Nóminas e Impuestos
        st.subheader("📊 Ciclo Económico")
        impuesto = st.number_input("Impuesto por ciclo (OI):", min_value=0, value=0)
        if st.button("💸 EJECUTAR CICLO"):
            recaudacion = 0
            for m in st.session_state.db:
                _, pago = obtener_datos_sc(st.session_state.db[m]["sc"])
                if m != "Juan":
                    st.session_state.db[m]["saldo"] += (pago - impuesto)
                    recaudacion += impuesto
                else:
                    st.session_state.db[m]["saldo"] += pago
            st.session_state.db["Juan"]["saldo"] += recaudacion
            st.balloons()
            st.rerun()

        # SISTEMA DE GUARDADO (EL REPORTE)
        st.write("---")
        st.subheader("💾 Guardar Progreso")
        if st.button("Generar Reporte de Saldo y S.C."):
            resumen = []
            for k, v in st.session_state.db.items():
                resumen.append({"Usuario": k, "Saldo": v["saldo"], "S.C.": v["sc"]})
            st.table(pd.DataFrame(resumen))
            st.info("Juan, copia estos datos en tu Excel. Si quieres que se queden fijos en la web al reiniciar, actualiza los números en el código de GitHub.")
