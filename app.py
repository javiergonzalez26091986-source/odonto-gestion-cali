import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaIoBaseUpload
import io

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Odontología Familiar Especializada", layout="wide")

# Estilo personalizado para que se vea profesional
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 5px; background-color: #007bff; color: white; }
    </style>
    """, unsafe_allow_html=True)

st.title("🦷 Gestión - Odontología Familiar Especializada")

# 2. CONEXIÓN A GOOGLE SHEETS
# Asegúrate de tener configurado [connections.gsheets] en los Secrets de Streamlit
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. FUNCIÓN PARA SUBIR IMÁGENES A GOOGLE DRIVE
def subir_a_drive(archivo, nombre_paciente):
    # Extraemos las credenciales de los Secrets de Streamlit
    creds_info = st.secrets["connections"]["gsheets"]
    creds = service_account.Credentials.from_service_account_info(creds_info)
    service = build('drive', 'v3', credentials=creds)
    
    # REEMPLAZA ESTO: Pon el ID de tu carpeta de Google Drive aquí
    ID_CARPETA_DRIVE = "TU_ID_DE_CARPETA_AQUI" 
    
    file_metadata = {
        'name': f"RAD_{nombre_paciente}_{archivo.name}",
        'parents': [ID_CARPETA_DRIVE]
    }
    media = MediaIoBaseUpload(io.BytesIO(archivo.getbuffer()), mimetype=archivo.type)
    
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    return file.get('id')

# 4. MENÚ LATERAL
menu = st.sidebar.selectbox("Seleccione un Módulo", ["Historia Clínica", "Radiografías y Fotos", "Facturación Interna"])

# --- MÓDULO: HISTORIA CLÍNICA ---
if menu == "Historia Clínica":
    st.header("📋 Registro de Pacientes")
    
    # Leer datos actuales de la pestaña 'Pacientes'
    df_pacientes = conn.read(worksheet="Pacientes")
    
    with st.form("form_paciente"):
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre Completo")
            cedula = st.text_input("Cédula/ID")
        with col2:
            telefono = st.text_input("Teléfono")
            fecha = st.date_input("Fecha de Consulta")
        
        diagnostico = st.text_area("Notas Médicas / Diagnóstico")
        
        if st.form_submit_button("Guardar Historia Clínica"):
            nueva_fila = pd.DataFrame([{
                "Nombre": nombre, 
                "Cédula": cedula, 
                "Teléfono": telefono, 
                "Fecha": str(fecha), 
                "Notas": diagnostico
            }])
            df_final = pd.concat([df_pacientes, nueva_fila], ignore_index=True)
            conn.update(worksheet="Pacientes", data=df_final)
            st.success(f"¡Historia de {nombre} guardada!")
    
    st.subheader("Pacientes en Base de Datos")
    st.dataframe(df_pacientes)

# --- MÓDULO: RADIOGRAFÍAS ---
elif menu == "Radiografías y Fotos":
    st.header("📸 Carga de Imágenes a Drive")
    nombre_p = st.text_input("Nombre del Paciente para el archivo")
    img = st.file_uploader("Subir Radiografía (JPG, PNG, PDF)", type=['png', 'jpg', 'jpeg', 'pdf'])
    
    if img and nombre_p:
        if st.button("Enviar a Google Drive"):
            with st.spinner("Subiendo archivo..."):
                id_foto = subir_a_drive(img, nombre_p)
                st.success(f"✅ Imagen guardada en Drive. ID del archivo: {id_foto}")

# --- MÓDULO: FACTURACIÓN ---
elif menu == "Facturación Interna":
    st.header("💸 Recibos de Caja")
    df_facturas = conn.read(worksheet="Facturacion")
    
    with st.form("form_factura"):
        cliente = st.text_input("Nombre del Cliente")
        servicio = st.selectbox("Tratamiento", ["Limpieza", "Resina", "Extracción", "Ortodoncia", "Otro"])
        valor = st.number_input("Valor ($)", min_value=0)
        
        if st.form_submit_button("Generar Factura"):
            nueva_factura = pd.DataFrame([{
                "Cliente": cliente, 
                "Servicio": servicio, 
                "Valor": valor, 
                "Fecha": str(pd.Timestamp.now())
            }])
            df_fact_final = pd.concat([df_facturas, nueva_factura], ignore_index=True)
            conn.update(worksheet="Facturacion", data=df_fact_final)
            st.info(f"Factura registrada por ${valor:,.0f}")
    
    st.subheader("Historial de Pagos")
    st.table(df_facturas.tail(5)) # Muestra las últimas 5 facturas
