import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from oauth2client.service_account import ServiceAccountCredentials

# --- CONFIGURACIÓN Y CONEXIÓN ---
st.set_page_config(page_title="Gestión Odontológica", page_icon="🦷")
st.title("🦷 Gestión - Odontología Familiar Especializada")

# ID de tu carpeta de Drive
ID_CARPETA = "1hauuaIMZOztMBJSUANg0Ce7kquOAqYEu"

# Conexión a Sheets (Lo que ya funciona)
conn = st.connection("gsheets", type=GSheetsConnection)
df_pacientes = conn.read(worksheet="Pacientes", ttl=0)

# --- FUNCIÓN PARA SUBIR A DRIVE ---
def subir_a_drive(archivo, nombre_archivo):
    try:
        # Usamos los mismos secretos que ya tienes en Streamlit
        scope = ['https://www.googleapis.com/auth/drive']
        dict_secrets = st.secrets["connections"]["gsheets"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(dict_secrets, scope)
        
        gauth = GoogleAuth()
        gauth.credentials = creds
        drive = GoogleDrive(gauth)
        
        # Crear el archivo en la carpeta específica
        f = drive.CreateFile({
            'title': nombre_archivo,
            'parents': [{'id': ID_CARPETA}]
        })
        f.SetContentString(archivo.getbuffer()) # Solo si es texto, para imagen usamos:
        # Corrección para imágenes:
        f.content = archivo
        f.Upload()
        
        # Retornar el link público (o de visualización)
        return f['alternateLink']
    except Exception as e:
        st.error(f"Error subiendo a Drive: {e}")
        return "ERROR_SUBIDA"

# --- MENÚ ---
menu = st.sidebar.selectbox(
    "Seleccione una opción", 
    ["Registro de Pacientes", "Evolución de Pacientes", "Facturacion Interna"]
)

# Módulo 1 y 3 se mantienen iguales (tu código funcional)
# ... [Código de Registro y Facturación] ...

# --- MÓDULO 2: EVOLUCIÓN (CON SUBIDA REAL) ---
if menu == "Evolución de Pacientes":
    st.header("📝 Evolución y Consultas")
    if not df_pacientes.empty:
        nombres_p = df_pacientes['Nombre'].unique().tolist()
        seleccion = st.selectbox("Seleccione el Paciente", [""] + nombres_p)
        
        if seleccion != "":
            datos_p = df_pacientes[df_pacientes['Nombre'] == seleccion].iloc[0]
            cedula_sel = datos_p['Cédula']
            
            with st.form("form_consulta"):
                f_consulta = st.date_input("Fecha", datetime.date.today())
                motivo = st.text_area("Motivo")
                diagnostico = st.text_area("Diagnóstico")
                tratamiento = st.text_area("Tratamiento")
                archivo_foto = st.file_uploader("Subir Radiografía", type=['jpg', 'png', 'jpeg'])
                
                if st.form_submit_button("Guardar Consulta"):
                    link_final = "SIN FOTO"
                    
                    if archivo_foto:
                        with st.spinner("Subiendo imagen a Google Drive..."):
                            nombre_it = f"Evid_{cedula_sel}_{f_consulta}.jpg"
                            # Lógica para subir el archivo físicamente
                            link_final = subir_a_drive(archivo_foto, nombre_it)
                    
                    nueva_consulta = pd.DataFrame([{
                        "Cédula": str(cedula_sel),
                        "Fecha": str(f_consulta),
                        "Motivo": motivo.upper(),
                        "Diagnóstico": diagnostico.upper(),
                        "Tratamiento": tratamiento.upper(),
                        "Link_Foto": link_final
                    }])
                    
                    conn.update(worksheet="Consultas", data=nueva_consulta)
                    st.success(f"Consulta guardada. Link de foto: {link_final}")
                    st.cache_data.clear()
