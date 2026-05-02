import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime
import os
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account

# --- CONFIGURACIÓN INICIAL ---
st.set_page_config(page_title="Gestión Odontológica", page_icon="🦷", layout="wide")
st.title("🦷 Gestión - Odontología Familiar Especializada")

# ID de tu carpeta de Drive (FOTOS_ODONTOLOGIA)
ID_CARPETA_DRIVE = "1hauuaIMZOztMBJSUANg0Ce7kquOAqYEu"

# --- CONEXIÓN A GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

def cargar_datos():
    try:
        pacientes = conn.read(worksheet="Pacientes", ttl=0)
        consultas = conn.read(worksheet="Consultas", ttl=0)
        facturacion = conn.read(worksheet="Facturacion", ttl=0)
        return pacientes, consultas, facturacion
    except Exception:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

df_pacientes, df_consultas, df_factura = cargar_datos()

# --- FUNCIÓN PARA SUBIR A DRIVE (VERSIÓN ORIGINAL) ---
def subir_a_drive(archivo_subido, nombre_archivo):
    try:
        creds_info = st.secrets["connections"]["gsheets"]
        creds = service_account.Credentials.from_service_account_info(creds_info)
        service = build('drive', 'v3', credentials=creds)
        
        temp_path = f"temp_{nombre_archivo}"
        with open(temp_path, "wb") as f:
            f.write(archivo_subido.getbuffer())
        
        file_metadata = {
            'name': nombre_archivo,
            'parents': [ID_CARPETA_DRIVE]
        }
        
        media = MediaFileUpload(temp_path, mimetype='image/jpeg')
        
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        
        os.remove(temp_path)
        return True
    except Exception as e:
        st.error(f"Error en Drive: {e}")
        return False

# --- MENÚ LATERAL ---
menu = st.sidebar.selectbox("Seleccione una opción", 
    ["Registro de Pacientes", "Evolución de Pacientes", "Facturacion Interna"])

# --- MÓDULO 1: REGISTRO ---
if menu == "Registro de Pacientes":
    st.header("📋 Registro de Nuevo Paciente")
    with st.form("form_registro", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre Completo")
            cedula = st.text_input("Cédula")
        with col2:
            tel = st.text_input("Teléfono")
            foto = st.file_uploader("Subir Foto de Perfil", type=['jpg', 'png', 'jpeg'])
        
        notas = st.text_area("Notas iniciales")
        
        if st.form_submit_button("Registrar Paciente"):
            if nombre and cedula and foto:
                nombre_foto = f"{cedula}_PERFIL.jpg"
                if subir_a_drive(foto, nombre_foto):
                    nuevo = pd.DataFrame([{
                        "Nombre": nombre.upper(),
                        "Cédula": str(cedula),
                        "Teléfono": str(tel),
                        "Fecha": str(datetime.date.today()),
                        "Notas": notas.upper(),
                        "Foto": "SUBIDA"
                    }])
                    conn.update(worksheet="Pacientes", data=nuevo)
                    st.success(f"✅ {nombre} registrado correctamente.")
                    st.cache_data.clear()
            else:
                st.warning("Por favor complete Nombre, Cédula y Foto.")

# --- MÓDULO 2: EVOLUCIÓN ---
elif menu == "Evolución de Pacientes":
    st.header("📝 Evolución y Consultas")
    if not df_pacientes.empty:
        nombres_lista = df_pacientes['Nombre'].dropna().unique().tolist()
        paciente_sel = st.selectbox("Seleccione el Paciente", [""] + nombres_lista)
        
        if paciente_sel != "":
            datos_p = df_pacientes[df_pacientes['Nombre'] == paciente_sel].iloc[0]
            cedula_p = str(datos_p['Cédula']).split('.')[0]
            
            col_hist, col_img = st.columns([1, 1])
            
            with col_hist:
                st.subheader("📜 Historial de Consultas")
                if not df_consultas.empty:
                    hist = df_consultas[df_consultas['Cédula'].astype(str).str.contains(cedula_p)]
                    if not hist.empty:
                        for _, fila in hist.iterrows():
                            with st.expander(f"Fecha: {fila['Fecha']}"):
                                st.write(f"**Motivo:** {fila['Motivo']}")
                                st.write(f"**Tratamiento:** {fila['Tratamiento']}")
                    else: st.info("No hay evoluciones.")

            with col_img:
                st.subheader("📸 Galería en Drive")
                st.markdown(f'<iframe src="https://drive.google.com/embeddedfolderview?id={ID_CARPETA_DRIVE}#grid" width="100%" height="400" frameborder="0"></iframe>', unsafe_allow_html=True)

            st.divider()
            with st.form("nueva_ev"):
                st.subheader("Registrar Nueva Evolución")
                f_ev = st.date_input("Fecha", datetime.date.today())
                motivo = st.text_area("Motivo")
                trata = st.text_area("Tratamiento")
                if st.form_submit_button("Guardar"):
                    nueva_fila = pd.DataFrame([{
                        "Cédula": str(cedula_p),
                        "Fecha": str(f_ev),
                        "Motivo": motivo.upper(),
                        "Tratamiento": trata.upper()
                    }])
                    conn.update(worksheet="Consultas", data=nueva_fila)
                    st.success("✅ Evolución guardada.")
                    st.cache_data.clear()

# --- MÓDULO 3: FACTURACIÓN ---
elif menu == "Facturacion Interna":
    st.header("💰 Facturación Interna")
    if not df_pacientes.empty:
        p_f = st.selectbox("Paciente", df_pacientes['Nombre'].tolist())
        with st.form("f_pago"):
            servicio = st.text_input("Servicio")
            valor = st.number_input("Valor", min_value=0, step=1000)
            if st.form_submit_button("Registrar Pago"):
                pago = pd.DataFrame([{
                    "Paciente": p_f, 
                    "Fecha": str(datetime.date.today()), 
                    "Servicio": servicio.upper(), 
                    "Valor": valor
                }])
                conn.update(worksheet="Facturacion", data=pago)
                st.success("✅ Pago registrado.")
                st.cache_data.clear()
