import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime
import cloudinary
import cloudinary.uploader

# --- CONFIGURACIÓN INICIAL ---
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

def cargar_datos():
    try:
        # worksheet="Pacientes" debe existir en tu Google Sheets
        return conn.read(worksheet="Pacientes", ttl=0)
    except:
        return pd.DataFrame()

def subir_a_cloudinary(archivo):
    try:
        resultado = cloudinary.uploader.upload(archivo)
        return resultado['secure_url']
    except Exception as e:
        st.error(f"Error al subir imagen: {e}")
        return None

# --- INTERFAZ ---
st.title("🦷 Odontología Familiar Especializada")

menu = st.sidebar.selectbox("Menú", ["Registro de Pacientes", "Ver Pacientes"])

if menu == "Registro de Pacientes":
    st.header("📋 Registro")
    with st.form("form_registro", clear_on_submit=True):
        nombre = st.text_input("Nombre Completo")
        cedula = st.text_input("Cédula")
        foto = st.file_uploader("Foto del Paciente", type=['jpg', 'png', 'jpeg'])
        
        if st.form_submit_button("Guardar Registro"):
            if nombre and cedula and foto:
                url_foto = subir_a_cloudinary(foto)
                if url_foto:
                    nueva_fila = pd.DataFrame([{
                        "Nombre": nombre.upper(),
                        "Cédula": str(cedula),
                        "Foto": url_foto,
                        "Fecha": str(datetime.date.today())
                    }])
                    conn.update(worksheet="Pacientes", data=nueva_fila)
                    st.success(f"✅ {nombre} registrado correctamente.")
            else:
                st.warning("Faltan datos obligatorios.")

elif menu == "Ver Pacientes":
    st.header("👥 Listado")
    df = cargar_datos()
    if not df.empty:
        st.dataframe(df)
        for index, row in df.iterrows():
            with st.expander(f"Paciente: {row['Nombre']}"):
                col1, col2 = st.columns([1, 2])
                with col1:
                    if row['Foto']:
                        st.image(row['Foto'], width=200)
                with col2:
                    st.write(f"**Cédula:** {row['Cédula']}")
                    st.write(f"**Fecha Registro:** {row['Fecha']}")
    else:
        st.info("No hay pacientes registrados aún.")
