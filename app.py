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
    st.info("Versión 1.3 - Gestión Odontológica")

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
# MÓDULO 2: EVOLUCIÓN Y GALERÍA (Aquí corregimos el KeyError)
# ---------------------------------------------------------
elif menu == "Evolución y Galería":
    st.title("📂 Historial y Evolución")
    try:
        # Forzamos la lectura fresca del Excel
        df = conn.read(worksheet="Pacientes", ttl=0)
        
        if not df.empty:
            busqueda = st.text_input("🔍 Buscar por Nombre o Cédula").upper()
            if busqueda:
                # Filtro seguro por nombre o cédula
                df = df[df['Nombre'].str.contains(busqueda, na=False) | df['Cédula'].astype(str).str.contains(busqueda, na=False)]
            
            for index, row in df.iterrows():
                # .get('Nombre', 'N/A') evita que la app se rompa si falta la columna
                nombre_p = row.get('Nombre', 'Sin nombre')
                cedula_p = row.get('Cédula', 'Sin ID')
                
                with st.expander(f"👤 {nombre_p} (CC: {cedula_p})"):
                    c1, c2 = st.columns([1, 2])
                    with c1:
                        # Verificamos si existe la columna 'Foto' y si tiene contenido
                        url_foto = row.get('Foto', None)
                        if url_foto and str(url_foto) != 'nan':
                            st.image(url_foto, caption="Registro Fotográfico")
                        else:
                            st.warning("No hay foto disponible.")
                    with c2:
                        # Usamos .get() para todas las columnas dudosas
                        st.write(f"**Teléfono:** {row.get('Teléfono', 'N/D')}")
                        st.write(f"**EPS:** {row.get('EPS', 'N/D')}")
                        st.write(f"**Fecha de Registro:** {row.get('Fecha_Registro', 'N/D')}")
                        st.write(f"**Observaciones:** {row.get('Observaciones', 'Sin observaciones registradas')}")
        else:
            st.info("No hay pacientes registrados en la base de datos.")
    except Exception as e:
        st.error(f"Error al cargar la base de datos: {e}")

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
