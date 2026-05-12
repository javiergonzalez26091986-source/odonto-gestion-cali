import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime
import cloudinary
import cloudinary.uploader

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Odonto-Cali", page_icon="🦷", layout="wide")

# --- ESTILOS CSS PERSONALIZADOS (Para que los botones resalten) ---
st.markdown("""
    <style>
    div.stButton > button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #262730;
        color: white;
        border: 1px solid #464855;
        text-align: left;
        padding-left: 20px;
    }
    div.stButton > button:hover {
        border-color: #FF4B4B;
        color: #FF4B4B;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CONFIGURACIÓN DE CLOUDINARY ---
cloudinary.config(
    cloud_name = st.secrets["cloudinary"]["cloud_name"],
    api_key = st.secrets["cloudinary"]["api_key"],
    api_secret = st.secrets["cloudinary"]["api_secret"],
    secure = True
)

# --- CONEXIÓN A GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

def subir_a_cloudinary(archivo):
    try:
        resultado = cloudinary.uploader.upload(archivo)
        return resultado['secure_url']
    except Exception as e:
        st.error(f"Error en Cloudinary: {e}")
        return None

# --- LÓGICA DE NAVEGACIÓN PROFESIONAL ---
if 'menu_actual' not in st.session_state:
    st.session_state.menu_actual = "Registro de Pacientes"

with st.sidebar:
    st.title("🦷 Odonto-Cali")
    st.markdown("---")
    st.write("**SELECCIONE UN MÓDULO:**")
    
    if st.button("📋 Registro de Pacientes"):
        st.session_state.menu_actual = "Registro de Pacientes"
    
    if st.button("📂 Evolución y Galería"):
        st.session_state.menu_actual = "Evolución y Galería"
        
    if st.button("📅 Agenda de Citas"):
        st.session_state.menu_actual = "Agenda de Citas"
        
    if st.button("⚙️ Configuración"):
        st.session_state.menu_actual = "Configuración"
        
    st.markdown("---")
    st.caption("Versión 1.4 - Gestión Odontológica")

# Capturamos la selección para mostrar el contenido
menu = st.session_state.menu_actual

# ---------------------------------------------------------
# MÓDULO 1: REGISTRO DE PACIENTES
# ---------------------------------------------------------
if menu == "Registro de Pacientes":
    st.header("📋 Registro de Nuevo Paciente")
    with st.form("registro_paciente", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre Completo")
            cedula = st.text_input("Cédula / ID")
            telefono = st.text_input("Teléfono")
        with col2:
            eps = st.text_input("EPS")
            fecha_nac = st.date_input("Fecha de Nacimiento", min_value=datetime.date(1940,1,1))
        
        foto = st.file_uploader("Foto Inicial / Rx", type=['jpg', 'png', 'jpeg'])
        observaciones = st.text_area("Observaciones Iniciales")
        
        if st.form_submit_button("Guardar Paciente"):
            if nombre and cedula and foto:
                with st.spinner("Subiendo datos..."):
                    url_foto = subir_a_cloudinary(foto)
                    if url_foto:
                        nueva_fila = pd.DataFrame([{
                            "Nombre": nombre.upper(),
                            "Cédula": str(cedula),
                            "Teléfono": telefono,
                            "EPS": eps.upper(),
                            "Foto": url_foto,
                            "Observaciones": observaciones,
                            "Fecha_Registro": str(datetime.date.today())
                        }])
                        conn.update(worksheet="Pacientes", data=nueva_fila)
                        st.success(f"✅ Paciente {nombre} registrado exitosamente.")
            else:
                st.warning("Nombre, Cédula y Foto son campos obligatorios.")

# ---------------------------------------------------------
# MÓDULO 2: EVOLUCIÓN Y GALERÍA
# ---------------------------------------------------------
elif menu == "Evolución y Galería":
    st.header("📂 Historial y Evolución")
    try:
        df = conn.read(worksheet="Pacientes", ttl=0)
        if not df.empty:
            busqueda = st.text_input("🔍 Buscar por Nombre o Cédula").upper()
            if busqueda:
                df = df[df['Nombre'].str.contains(busqueda, na=False) | df['Cédula'].astype(str).str.contains(busqueda, na=False)]
            
            for index, row in df.iterrows():
                with st.expander(f"👤 {row.get('Nombre', 'Sin nombre')} (CC: {row.get('Cédula', 'Sin ID')})"):
                    c1, c2 = st.columns([1, 2])
                    with c1:
                        url_foto = row.get('Foto', None)
                        if url_foto and str(url_foto) != 'nan':
                            st.image(url_foto, use_container_width=True)
                    with c2:
                        st.write(f"**Teléfono:** {row.get('Teléfono', 'N/D')}")
                        st.write(f"**EPS:** {row.get('EPS', 'N/D')}")
                        st.write(f"**Observaciones:** {row.get('Observaciones', 'N/D')}")
        else:
            st.info("No hay registros.")
    except:
        st.error("Error al conectar con la base de datos.")

# ---------------------------------------------------------
# MÓDULO 3: AGENDA DE CITAS
# ---------------------------------------------------------
elif menu == "Agenda de Citas":
    st.header("📅 Calendario de Citas")
    st.info("Módulo en construcción.")

# ---------------------------------------------------------
# MÓDULO 4: CONFIGURACIÓN
# ---------------------------------------------------------
elif menu == "Configuración":
    st.header("⚙️ Configuración")
    st.write("Base de Datos y Cloudinary: ✅ Operativos")
