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

# --- BARRA LATERAL (MENÚ) ---
with st.sidebar:
    st.title("🦷 Odonto-Cali")
    st.markdown("---")
    menu = st.radio(
        "SELECCIONE UN MÓDULO:",
        ["Registro de Pacientes", "Evolución y Galería", "Agenda de Citas", "Configuración"],
        index=0
    )
    st.markdown("---")
    st.info("Versión 1.2 - Gestión Odontológica")

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
    st.title("📂 Historial y Evolución")
    df = conn.read(worksheet="Pacientes", ttl=0)
    
    if not df.empty:
        busqueda = st.text_input("🔍 Buscar por Nombre o Cédula").upper()
        if busqueda:
            df = df[df['Nombre'].str.contains(busqueda) | df['Cédula'].astype(str).str.contains(busqueda)]
        
        for index, row in df.iterrows():
            with st.expander(f"👤 {row['Nombre']} (CC: {row['Cédula']})"):
                c1, c2 = st.columns([1, 2])
                with c1:
                    if row['Foto']:
                        st.image(row['Foto'], caption="Registro Fotográfico")
                with c2:
                    st.write(f"**Teléfono:** {row['Teléfono']}")
                    st.write(f"**EPS:** {row['EPS']}")
                    st.write(f"**Fecha de Registro:** {row['Fecha_Registro']}")
                    st.write(f"**Observaciones:** {row['Observaciones']}")
    else:
        st.info("No hay pacientes registrados en la base de datos.")

# ---------------------------------------------------------
# MÓDULO 3: AGENDA DE CITAS
# ---------------------------------------------------------
elif menu == "Agenda de Citas":
    st.title("📅 Calendario de Citas")
    st.info("Módulo en construcción. Próximamente integración con el registro.")

# ---------------------------------------------------------
# MÓDULO 4: CONFIGURACIÓN
# ---------------------------------------------------------
elif menu == "Configuración":
    st.title("⚙️ Configuración")
    st.write("Base de Datos (Google Sheets): ✅ Conectado")
    st.write("Almacenamiento (Cloudinary): ✅ Conectado")
