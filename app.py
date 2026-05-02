import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from google.oauth2 import service_account
import os

# --- CONFIGURACIÓN INICIAL ---
ID_CARPETA_DRIVE = "TU_ID_DE_CARPETA_AQUÍ"  # Reemplaza con el ID de tu carpeta de Drive

st.set_page_config(page_title="Gestión Odontológica - Odonto Cali", layout="wide")
st.title("🦷 Sistema de Gestión - Odonto Cali")

# --- CONEXIÓN A GOOGLE SHEETS ---
# Utiliza la configuración [connections.gsheets] de tus Secrets
conn = st.connection("gsheets", type=GSheetsConnection)

def leer_datos(pestaña):
    return conn.read(worksheet=pestaña)

# --- FUNCIÓN PARA DRIVE (USANDO SECRETS) ---
def subir_a_drive(archivo_subido, nombre_archivo):
    try:
        # Definimos el alcance (scope) para Google Drive
        scope = ['https://www.googleapis.com/auth/drive']
        
        # Leemos las credenciales directamente desde los Secrets de Streamlit
        # Esto evita el error: [Errno 2] No such file or directory: 'credentials.json'
        creds_info = st.secrets["connections"]["gsheets"]
        creds = service_account.Credentials.from_service_account_info(
            creds_info, scopes=scope)
        
        # Configuración de PyDrive2 con las credenciales de memoria
        gauth = GoogleAuth()
        gauth.credentials = creds
        drive = GoogleDrive(gauth)
        
        # Crear el archivo en la carpeta específica
        f = drive.CreateFile({
            'title': nombre_archivo,
            'parents': [{'id': ID_CARPETA_DRIVE}]
        })
        
        # Guardado temporal para la transferencia
        temp_path = f"temp_{nombre_archivo}"
        with open(temp_path, "wb") as tmp:
            tmp.write(archivo_subido.getbuffer())
        
        f.SetContentFile(temp_path)
        f.Upload()
        os.remove(temp_path)  # Limpiar archivo temporal
        return True
    except Exception as e:
        st.error(f"Error crítico en Drive: {e}")
        return False

# --- INTERFAZ DE USUARIO (EJEMPLO DE REGISTRO) ---
menu = ["Registro de Pacientes", "Consultas y Fotos", "Ver Base de Datos"]
choice = st.sidebar.selectbox("Menú", menu)

if choice == "Registro de Pacientes":
    st.subheader("Registrar Nuevo Paciente")
    with st.form("form_paciente"):
        nombre = st.text_input("Nombre Completo")
        cedula = st.text_input("Cédula/ID")
        telefono = st.text_input("Teléfono")
        submit = st.form_submit_button("Guardar Paciente")
        
        if submit:
            # Aquí iría tu lógica para actualizar el DataFrame y conn.update()
            st.success(f"Paciente {nombre} registrado con éxito.")

elif choice == "Consultas y Fotos":
    st.subheader("Cargar Foto de Consulta")
    foto = st.file_uploader("Seleccione la imagen del tratamiento", type=["jpg", "png", "jpeg"])
    nombre_paciente = st.text_input("Nombre del archivo (ej: Juan_Perez_Tratamiento.jpg)")
    
    if st.button("Subir a Google Drive"):
        if foto is not None and nombre_paciente:
            con_exito = subir_a_drive(foto, nombre_paciente)
            if con_exito:
                st.success("✅ Foto subida correctamente a Google Drive.")
        else:
            st.warning("Por favor cargue una foto y asigne un nombre.")

elif choice == "Ver Base de Datos":
    st.subheader("Listado de Pacientes")
    try:
        df = leer_datos("Pacientes")
        st.dataframe(df)
    except Exception as e:
        st.error(f"No se pudo leer la hoja 'Pacientes': {e}")
