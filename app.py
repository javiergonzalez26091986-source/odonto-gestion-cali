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

# ID de la carpeta de Drive proporcionada
ID_CARPETA = "1hauuaIMZOztMBJSUANg0Ce7kquOAqYEu"

# --- FUNCIÓN DE SUBIDA A DRIVE ---
def subir_archivo_drive(archivo_subido, nombre_archivo):
    try:
        info_claves = st.secrets["connections"]["gsheets"]
        creds = service_account.Credentials.from_service_account_info(info_claves)
        service = build('drive', 'v3', credentials=creds)
        
        file_metadata = {'name': nombre_archivo, 'parents': [ID_CARPETA]}
        media = MediaIoBaseUpload(io.BytesIO(archivo_subido.getvalue()), mimetype=archivo_subido.type)
        
        file = service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()
        return file.get('webViewLink')
    except Exception as e:
        st.error(f"Error en Drive: {e}")
        return "ERROR_SUBIDA"

# --- CONEXIÓN A SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)
df_pacientes = conn.read(worksheet="Pacientes", ttl=0)

menu = st.sidebar.selectbox("Seleccione una opción", ["Registro de Pacientes", "Evolución de Pacientes", "Facturacion Interna"])

# --- MÓDULO 1: REGISTRO DE PACIENTES ---
if menu == "Registro de Pacientes":
    st.header("📋 Registro de Nuevo Paciente")
    with st.form("form_reg"):
        nombre = st.text_input("Nombre Completo")
        cedula = st.text_input("Cédula")
        tel = st.text_input("Teléfono")
        fecha_reg = st.date_input("Fecha de Registro", datetime.date.today())
        # CAMPO DE FOTO RESTAURADO
        foto_perfil = st.file_uploader("Subir Foto de Perfil / Documento", type=['jpg', 'png', 'jpeg'])
        nota = st.text_area("Notas")
        
        if st.form_submit_button("Registrar Paciente"):
            if nombre and cedula:
                link_foto_perfil = "SIN FOTO"
                if foto_perfil:
                    with st.spinner("Subiendo foto de perfil..."):
                        nombre_f = f"Perfil_{cedula}_{datetime.date.today()}.jpg"
                        link_foto_perfil = subir_archivo_drive(foto_perfil, nombre_f)
                
                nuevo = pd.DataFrame([{
                    "Nombre": nombre.upper(), 
                    "Cédula": str(cedula), 
                    "Teléfono": str(tel), 
                    "Fecha": str(fecha_reg), 
                    "Notas": nota.upper(),
                    "Foto": link_foto_perfil # Campo para la pestaña Pacientes
                }])
                conn.update(worksheet="Pacientes", data=nuevo)
                st.success(f"✅ Paciente registrado. Foto: {link_foto_perfil}")
                st.cache_data.clear()

# --- MÓDULO 2: EVOLUCIÓN DE PACIENTES ---
elif menu == "Evolución de Pacientes":
    st.header("📝 Evolución y Consultas")
    if not df_pacientes.empty:
        lista_nombres = df_pacientes['Nombre'].unique().tolist()
        sel = st.selectbox("Paciente", [""] + lista_nombres)
        
        if sel != "":
            cedula_p = df_pacientes[df_pacientes['Nombre'] == sel]['Cédula'].values[0]
            with st.form("form_ev"):
                f_ev = st.date_input("Fecha Consulta", datetime.date.today())
                motivo = st.text_area("Motivo")
                diag = st.text_area("Diagnóstico")
                trata = st.text_area("Tratamiento")
                # CAMPO DE FOTO RESTAURADO
                foto_ev = st.file_uploader("Subir Radiografía / Foto del día", type=['jpg', 'png', 'jpeg'])
                
                if st.form_submit_button("Guardar Evolución"):
                    link_ev = "SIN FOTO"
                    if foto_ev:
                        with st.spinner("Subiendo evidencia a Drive..."):
                            nombre_ev = f"Evid_{cedula_p}_{f_ev}.jpg"
                            link_ev = subir_archivo_drive(foto_ev, nombre_ev)
                    
                    nueva_ev = pd.DataFrame([{
                        "Cédula": str(cedula_p),
                        "Fecha": str(f_ev),
                        "Motivo": motivo.upper(),
                        "Diagnóstico": diag.upper(),
                        "Tratamiento": trata.upper(),
                        "Link_Foto": link_ev
                    }])
                    conn.update(worksheet="Consultas", data=nueva_ev)
                    st.success(f"✅ Consulta guardada. Link: {link_ev}")
                    st.cache_data.clear()

# --- MÓDULO 3: FACTURACIÓN ---
elif menu == "Facturacion Interna":
    st.header("💰 Facturación")
    if not df_pacientes.empty:
        p_f = st.selectbox("Paciente", df_pacientes['Nombre'].unique().tolist())
        with st.form("f_pago"):
            serv = st.text_input("Servicio")
            val = st.number_input("Valor", min_value=0)
            if st.form_submit_button("Registrar Pago"):
                pago = pd.DataFrame([{"Paciente": p_f, "Fecha": str(datetime.date.today()), "Servicio": serv.upper(), "Valor": val}])
                conn.update(worksheet="Facturacion", data=pago)
                st.success("✅ Pago registrado.")
                st.cache_data.clear()
