import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime
import cloudinary
import cloudinary.uploader

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Odonto-Cali", page_icon="🦷")

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

st.title("🦷 Sistema de Gestión Odonto-Cali")

# --- FORMULARIO COMPLETO ---
with st.form("registro_paciente", clear_on_submit=True):
    st.subheader("Datos Personales")
    col1, col2 = st.columns(2)
    
    with col1:
        nombre = st.text_input("Nombre Completo")
        cedula = st.text_input("Cédula / ID")
        telefono = st.text_input("Teléfono de contacto")
    
    with col2:
        fecha_nacimiento = st.date_input("Fecha de Nacimiento", min_value=datetime.date(1920, 1, 1))
        eps = st.text_input("EPS / Aseguradora")
        genero = st.selectbox("Género", ["Masculino", "Femenino", "Otro"])

    st.subheader("Información Clínica")
    motivo = st.text_area("Motivo de la consulta")
    foto = st.file_uploader("Fotografía del paciente / Rx", type=['jpg', 'png', 'jpeg'])
    
    enviar = st.form_submit_button("Registrar Paciente")

    if enviar:
        if nombre and cedula and foto:
            with st.spinner("Guardando información..."):
                url_foto = subir_a_cloudinary(foto)
                
                if url_foto:
                    # Preparamos la fila con TODOS los campos
                    nueva_fila = pd.DataFrame([{
                        "Nombre": nombre.upper(),
                        "Cédula": str(cedula),
                        "Teléfono": telefono,
                        "Fecha_Nacimiento": str(fecha_nacimiento),
                        "EPS": eps.upper(),
                        "Género": genero,
                        "Motivo": motivo,
                        "Foto": url_foto,
                        "Fecha_Registro": str(datetime.date.today())
                    }])
                    
                    # Guardamos en la pestaña "Pacientes"
                    conn.update(worksheet="Pacientes", data=nueva_fila)
                    st.success(f"✅ Paciente {nombre} registrado con éxito.")
        else:
            st.warning("Por favor completa los campos obligatorios: Nombre, Cédula y Foto.")
