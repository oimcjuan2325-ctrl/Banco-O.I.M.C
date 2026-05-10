import streamlit as st
import pandas as pd
import math

# 1. CONFIGURACIÓN
st.set_page_config(page_title="O.I.M.C. Banco Real", page_icon="🏛️", layout="wide")

# 2. ENLACE A TU TABLA (Usa el enlace de "Publicar como CSV" si puedes)
# Si no, usa el normal de compartir asegurándote de que sea público
URL_CSV = "https://docs.google.com/spreadsheets/d/1tfFblkVs5AcPGQFXHIv9lHE2I8MKvZTc-yApAnEWKRc/edit?usp=sharing"

@st.cache_data(ttl=0)
def cargar_datos():
    # Convertimos el enlace de compartir normal a enlace de descarga directa si es necesario
    if "edit?" in URL_CSV:
        csv_url = URL_CSV.replace("edit?usp=sharing", "export?format=csv")
        csv_url = csv_url.replace("edit#gid=0", "export?format=csv")
    else:
        csv_url = URL_CSV
    return pd.read_csv(csv_url)

# Intentar cargar los datos
try:
    if 'df' not in st.session_state:
        st.session_state.df = cargar_datos()
except:
    st.error("Error al conectar con Google Sheets. Revisa el enlace.")
    st.stop()

# Lógica salarial según tu foto
def calcular_sueldo(sc):
    if sc >= 90: return 5
    elif sc >= 70: return 4
    elif sc >= 50: return 2
    else: return 0

# 3. LOGIN
if 'logeado' not in st.session_state:
    st.title("🏛️ O.I.M.C. - Iniciar Sesión")
    usuarios = st.session_state.df["Usuario"].tolist()
    nombre = st.selectbox("Selecciona tu cuenta", usuarios)
    pin_ingresado = st.text_input("Introduce tu PIN", type="password")
    
    if st.button("Acceder"):
        pin_real = str(st.session_state.df.loc[st.session_state.df["Usuario"] == nombre, "PIN"].values[0])
        if pin_ingresado == pin_real:
            st.session_state.logeado = nombre
            st.rerun()
        else:
            st.error("PIN incorrecto")
else:
    u_id = st.session_state.logeado
    fila = st.session_state.df[st.session_state.df["Usuario"] == u_id]
    
    # BARRA LATERAL
    with st.sidebar:
        st.title(f"👤 {u_id}")
        if st.button("Cerrar Sesión"):
            del st.session_state.logeado
            st.rerun()
        st.divider()
        st.info("Para cambios permanentes (PIN, Saldo, SC), pídelo al Gobernador.")

    # CUERPO
    st.title("📊 Mi Cuenta Bancaria")
    
    col1, col2, col3 = st.columns(3)
    saldo = int(fila["Saldo"].values[0])
    sc = int(fila["SC"].values[0])
    sueldo = calcular_sueldo(sc)
    
    col1.metric("Saldo Disponible", f"{saldo} OI")
    col2.metric("Social Credit", f"{sc} SC")
    col3.metric("Sueldo Próximo", f"{sueldo} OI")

    st.divider()

    # ENVÍOS (Solo visual en esta versión para evitar bloqueos de escritura de Google)
    st.subheader("💸 Enviar Fondos")
    st.write("Anota la transferencia y confirma con el Gobernador para que se registre en el libro mayor.")
    dest = st.selectbox("Enviar a:", [n for n in st.session_state.df["Usuario"].tolist() if n != u_id])
    cant = st.number_input("Cantidad", min_value=1, step=1)
    if st.button("Solicitar Envío"):
        st.success(f"Solicitud de envío de {cant} OI a {dest} enviada al sistema.")

    # PANEL DE JUAN
    if fila["Rol"].values[0] == "admin":
        st.divider()
        st.header("👑 Panel de Gobernador")
        st.write("Como los permisos de Google son estrictos, edita los valores directamente en el Google Sheets para que se actualicen aquí al instante.")
        st.link_button("Abrir Libro Mayor (Google Sheets)", URL_CSV)
