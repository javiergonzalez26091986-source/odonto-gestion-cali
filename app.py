import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Gestión Odontológica", page_icon="🦷")
st.title("🦷 Gestión - Odontología Familiar Especializada")

ID_CARPETA = "1hauuaIMZOztMBJSUANg0Ce7kquOAqYEu"

# --- CONEXIÓN A GOOGLE DRIVE (SUBIDA AUTOMÁTICA) ---
def subir_archivo_drive(archivo_subido, nombre_archivo):
    try:
        # Usamos las mismas credenciales de los Secrets de Streamlit
        info_claves = st.secrets["connections"]["gsheets"]
        creds = service_account.Credentials.from_service_account_info(info_claves)
        service = build('drive', 'v3', credentials=creds)
        
        file_metadata = {
            'name': nombre_archivo,
            'parents': [ID_CARPETA]
        }
        
        # Convertir el archivo de Streamlit a un formato que Drive entienda
        media = MediaIoBaseUpload(io.BytesIO(archivo_subido.getvalue()), 
                                  mimetype=archivo_subido.type)
        
        file = service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()
        return file.get('webViewLink')
    except Exception as e:
        st.error(f"Error subiendo a Drive: {e}")
        return "ERROR_SUBIDA"

# --- CONEXIÓN A SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)
df_pacientes = conn.read(worksheet="Pacientes", ttl=0)

menu = st.sidebar.selectbox("Seleccione una opción", ["Registro de Pacientes", "Evolución de Pacientes", "Facturacion Interna"])

# --- MÓDULO 1: REGISTRO ---
if menu == "Registro de Pacientes":
    st.header("📋 Registro de Nuevo Paciente")
    with st.form("form_reg"):
        nombre = st.text_input("Nombre Completo")
        cedula = st.text_input("Cédula")
        tel = st.text_input("Teléfono")
        nota = st.text_area("Notas")
        if st.form_submit_button("Registrar"):
            if nombre and cedula:
                nuevo = pd.DataFrame([{"Nombre": nombre.upper(), "Cédula": str(cedula), "Teléfono": str(tel), "Fecha": str(datetime.date.today()), "Notas": nota.upper()}])
                conn.update(worksheet="Pacientes", data=nuevo)
                st.success("✅ Paciente registrado.")
                st.cache_data.clear()

# --- MÓDULO 2: EVOLUCIÓN (CON SUBIDA DIRECTA) ---
elif menu == "Evolución de Pacientes":
    st.header("📝 Evolución y Consultas")
    if not df_pacientes.empty:
        lista_nombres = df_pacientes['Nombre'].unique().tolist()
        sel = st.selectbox("Paciente", [""] + lista_nombres)
        
        if sel != "":
            cedula_p = df_pacientes[df_pacientes['Nombre'] == sel]['Cédula'].values[0]
            with st.form("form_ev"):
                motivo = st.text_area("Motivo")
                diag = st.text_area("Diagnóstico")
                trata = st.text_area("Tratamiento")
                foto = st.file_uploader("Subir Radiografía/Foto", type=['jpg', 'png', 'jpeg'])
                
                if st.form_submit_button("Guardar Consulta y Subir Foto"):
                    link_drive = "SIN FOTO"
                    if foto:
                        with st.spinner("Subiendo imagen a Drive..."):
                            nombre_archivo = f"Odonto_{cedula_p}_{datetime.date.today()}.jpg"
                            link_drive = subir_archivo_drive(foto, nombre_archivo)
                    
                    nueva_ev = pd.DataFrame([{
                        "Cédula": str(cedula_p),
                        "Fecha": str(datetime.date.today()),
                        "Motivo": motivo.upper(),
                        "Diagnóstico": diag.upper(),
                        "Tratamiento": trata.upper(),
                        "Link_Foto": link_drive
                    }])
                    conn.update(worksheet="Consultas", data=nueva_ev)
                    st.success(f"✅ Guardado. Link: {link_drive}")
                    st.cache_data.clear()

# --- MÓDULO 3: FACTURACIÓN ---
elif menu == "Facturacion Interna":
    st.header("💰 Facturación")
    if not df_pacientes.empty:
        p_f = st.selectbox("Paciente", df_pacientes['Nombre'].unique().tolist())
        with st.form("f_pago"):
            serv = st.text_input("Servicio")
            val = st.number_input("Valor", min_value=0)
            if st.form_submit_button("Cobrar"):
                pago = pd.DataFrame([{"Paciente": p_f, "Fecha": str(datetime.date.today()), "Servicio": serv.upper(), "Valor": val}])
                conn.update(worksheet="Facturacion", data=pago)
                st.success("✅ Pago registrado.")
                st.cache_data.clear()
