import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime
import cloudinary
import cloudinary.uploader

# --- CONFIGURACIÓN DE CLOUDINARY ---
# Esto usa los datos que ya pegaste en los Secrets
cloudinary.config(
    cloud_name = st.secrets["cloudinary"]["cloud_name"],
    api_key = st.secrets["cloudinary"]["api_key"],
    api_secret = st.secrets["cloudinary"]["api_secret"],
    secure = True
)

# --- CONEXIÓN A GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

# Función para subir la imagen a Cloudinary
def subir_a_cloudinary(archivo):
    try:
        resultado = cloudinary.uploader.upload(archivo)
        return resultado['secure_url'] # Nos devuelve el link de la foto
    except Exception as e:
        st.error(f"Error al subir a Cloudinary: {e}")
        return None

st.title("🦷 Odonto-Cali: Gestión de Pacientes")

# --- FORMULARIO DE REGISTRO ---
with st.form("registro_paciente"):
    nombre = st.text_input("Nombre del Paciente")
    cedula = st.text_input("Cédula")
    foto = st.file_uploader("Subir foto", type=['jpg', 'png', 'jpeg'])
    
    if st.form_submit_button("Registrar"):
        if nombre and cedula and foto:
            # 1. Subimos la foto a Cloudinary (NO a Google Drive)
            url_foto = subir_a_cloudinary(foto)
            
            if url_foto:
                # 2. Guardamos los datos y el LINK de la foto en el Excel
                nueva_fila = pd.DataFrame([{
                    "Nombre": nombre.upper(),
                    "Cédula": str(cedula),
                    "Foto_URL": url_foto,
                    "Fecha": str(datetime.date.today())
                }])
                conn.update(worksheet="Pacientes", data=nueva_fila)
                st.success("✅ Paciente registrado con éxito. Foto guardada en la nube.")
        else:
            st.warning("Por favor, completa todos los campos.")
