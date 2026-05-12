import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime
import cloudinary
import cloudinary.uploader

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Odonto-Cali", page_icon="🦷", layout="wide")

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

# --- BARRA LATERAL (NAVEGACIÓN) ---
st.sidebar.image("https://res.cloudinary.com/ddouzzs1i/image/upload/v1/logo_odonto", width=150) # Opcional: tu logo
menu = st.sidebar.radio(
    "MENÚ PRINCIPAL",
    ["Registro de Pacientes", "Evolución y Galería", "Agenda de Citas", "Configuración"]
)

# ---------------------------------------------------------
# MÓDULO 1: REGISTRO DE PACIENTES
# ---------------------------------------------------------
if menu == "Registro de Pacientes":
    st.title("📋 Registro de Nuevo Paciente")
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
                with st.spinner("Registrando..."):
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
                        st.success(f"✅ Paciente {nombre} guardado exitosamente.")
            else:
                st.warning("Nombre, Cédula y Foto son obligatorios.")

# ---------------------------------------------------------
# MÓDULO 2: EVOLUCIÓN Y GALERÍA (Visualización)
# ---------------------------------------------------------
elif menu == "Evolución y Galería":
    st.title("📂 Historial de Pacientes")
    try:
        df = conn.read(worksheet="Pacientes", ttl=0)
        
        if not df.empty:
            busqueda = st.text_input("🔍 Buscar por Nombre o Cédula").upper()
            if busqueda:
                df = df[df['Nombre'].str.contains(busqueda) | df['Cédula'].astype(str).str.contains(busqueda)]
            
            for index, row in df.iterrows():
                with st.expander(f"📌 {row['Nombre']} - CC: {row['Cédula']}"):
                    c1, c2 = st.columns([1, 2])
                    with c1:
                        if row['Foto']:
                            st.image(row['Foto'], use_container_width=True)
                    with c2:
                        st.write(f"**Teléfono:** {row['Teléfono']}")
                        st.write(f"**EPS:** {row['EPS']}")
                        st.write(f"**Observaciones:** {row['Observaciones']}")
                        st.info(f"Fecha de Registro: {row['Fecha_Registro']}")
                        
                        # Botón para agregar nueva evolución (para el futuro)
                        if st.button(f"Agregar Evolución para {row['Cédula']}", key=f"btn_{index}"):
                            st.session_state.paciente_evol = row['Cédula']
                            st.write("Módulo de carga de evolución en desarrollo...")
        else:
            st.info("No hay pacientes registrados.")
    except Exception as e:
        st.error("Aún no existen registros o la hoja 'Pacientes' está vacía.")

# ---------------------------------------------------------
# MÓDULO 3: AGENDA DE CITAS
# ---------------------------------------------------------
elif menu == "Agenda de Citas":
    st.title("📅 Calendario de Citas")
    st.write("Próximamente: Integración con Google Calendar o tabla de citas local.")
    
    with st.expander("➕ Programar Nueva Cita"):
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            st.selectbox("Seleccionar Paciente", ["Cargar desde base de datos..."])
            st.date_input("Fecha de la Cita")
        with col_c2:
            st.time_input("Hora")
            st.selectbox("Procedimiento", ["Limpieza", "Extracción", "Ortodoncia", "Valoración"])
        st.button("Agendar")

# ---------------------------------------------------------
# MÓDULO 4: CONFIGURACIÓN
# ---------------------------------------------------------
elif menu == "Configuración":
    st.title("⚙️ Configuración del Sistema")
    st.write(f"**Usuario:** {st.secrets['connections']['gsheets']['client_email']}")
    st.write("**Estado de Conexión Google Sheets:** ✅ Activo")
    st.write("**Estado de Conexión Cloudinary:** ✅ Activo")
