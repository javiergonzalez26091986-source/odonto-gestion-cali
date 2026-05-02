import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime
import base64
from PIL import Image
import io

st.set_page_config(page_title="Gestión Odontológica", page_icon="🦷")
st.title("🦷 Gestión - Odontología Familiar Especializada")

conn = st.connection("gsheets", type=GSheetsConnection)

def preparar_imagen_base64(archivo_subido):
    # Abrimos la imagen y la redimensionamos para que no exceda el límite de la celda de Sheets
    img = Image.open(archivo_subido)
    img.thumbnail((200, 200)) # Tamaño pequeño para que quepa en el límite de caracteres
    
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=70)
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return f"data:image/jpeg;base64,{img_str}"

menu = st.sidebar.selectbox("Seleccione", ["Registro de Pacientes"])

if menu == "Registro de Pacientes":
    with st.form("form_reg"):
        nombre = st.text_input("Nombre Completo")
        cedula = st.text_input("Cédula")
        foto_perfil = st.file_uploader("Subir Foto", type=['jpg', 'png', 'jpeg'])
        
        if st.form_submit_button("Registrar"):
            if nombre and cedula:
                txt_foto = "SIN FOTO"
                if foto_perfil:
                    txt_foto = preparar_imagen_base64(foto_perfil)
                
                nuevo = pd.DataFrame([{
                    "Nombre": nombre.upper(), 
                    "Cédula": str(cedula), 
                    "Foto_Base64": txt_foto
                }])
                
                conn.update(worksheet="Pacientes", data=nuevo)
                st.success("✅ Datos y foto guardados en el Sheets.")
            else:
                st.error("Faltan datos.")
