import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime
import cloudinary
import cloudinary.uploader
import base64

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Odonto-Cali", page_icon="🦷", layout="wide")

# --- 1. FUNCIÓN PARA EL LOGO LOCAL (Base64) ---
def get_base64_logo(path):
    try:
        with open(path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except:
        return None

logo_base64 = get_base64_logo("logo_odontología_familiar.jpg")

# --- ESTILOS CSS PERSONALIZADOS ---
st.markdown("""
    <style>
    div.stButton > button {
        width: 100%;
        border-radius: 8px;
        height: 3.5em;
        background-color: #1E1E1E;
        color: white;
        border: 1px solid #3d3d3d;
        text-align: left;
        padding-left: 20px;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    div.stButton > button:hover {
        border-color: #00AEEF;
        color: #00AEEF;
        background-color: #262626;
        transform: translateX(5px);
    }
    </style>
    """, unsafe_allow_html=True)

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

# --- LÓGICA DE NAVEGACIÓN ---
if 'menu_actual' not in st.session_state:
    st.session_state.menu_actual = "Registro de Pacientes"

with st.sidebar:
    if logo_base64:
        st.markdown(
            f"""
            <div style="display: flex; justify-content: center; padding-bottom: 20px;">
                <img src="data:image/jpeg;base64,{logo_base64}" style="width: 100%; border-radius: 10px;">
            </div>
            """, 
            unsafe_allow_html=True
        )
    else:
        st.title("🦷 Odonto-Cali")
    
    st.write("**MENÚ DE GESTIÓN**")
    if st.button("📋 Registro de Pacientes"):
        st.session_state.menu_actual = "Registro de Pacientes"
    if st.button("📂 Evolución y Galería"):
        st.session_state.menu_actual = "Evolución y Galería"
    if st.button("📅 Agenda de Citas"):
        st.session_state.menu_actual = "Agenda de Citas"
    if st.button("⚙️ Configuración"):
        st.session_state.menu_actual = "Configuración"
    st.markdown("---")
    st.caption("Odontología Familiar Especializada v1.8")

menu = st.session_state.menu_actual

# ---------------------------------------------------------
# MÓDULO 1: REGISTRO DE PACIENTES
# ---------------------------------------------------------
if menu == "Registro de Pacientes":
    st.header("📋 Registro de Nuevo Paciente")
    with st.form("registro_paciente", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre Completo")
            cedula = st.text_input("Cédula / ID")
            telefono = st.text_input("Teléfono")
        with col2:
            eps = st.text_input("EPS")
            fecha_nac = st.date_input("Fecha de Nacimiento", min_value=datetime.date(1940,1,1))
        
        # AQUÍ ESTÁN TODOS LOS FORMATOS INCLUYENDO JFIF
        foto = st.file_uploader(
            "Foto Inicial / Rx / Documentos", 
            type=['jpg', 'png', 'jpeg', 'jfif', 'webp', 'bmp', 'heic', 'pdf', 'tiff']
        )
        observaciones = st.text_area("Observaciones Iniciales")
        
        if st.form_submit_button("Guardar Paciente"):
            if nombre and cedula and foto:
                with st.spinner("Subiendo datos e imagen..."):
                    url_foto = subir_a_cloudinary(foto)
                    if url_foto:
                        nueva_fila = pd.DataFrame([{
                            "Nombre": nombre.upper(),
                            "Cédula": str(cedula),
                            "Teléfono": telefono,
                            "EPS": eps.upper(),
                            "Foto": url_foto,
                            "Observaciones": observaciones,
                            "Fecha_Registro": str(datetime.date.today())
                        }])
                        conn.update(worksheet="Pacientes", data=nueva_fila)
                        st.success(f"✅ Paciente {nombre} registrado exitosamente.")
            else:
                st.warning("Nombre, Cédula y Foto son obligatorios.")

# ---------------------------------------------------------
# MÓDULO 2: EVOLUCIÓN Y GALERÍA
# ---------------------------------------------------------
elif menu == "Evolución y Galería":
    st.header("📂 Historial y Evolución")
    try:
        df = conn.read(worksheet="Pacientes", ttl=0)
        if not df.empty:
            busqueda = st.text_input("🔍 Buscar por Nombre o Cédula").upper()
            if busqueda:
                df = df[df['Nombre'].str.contains(busqueda, na=False) | df['Cédula'].astype(str).str.contains(busqueda, na=False)]
            
            for index, row in df.iterrows():
                with st.expander(f"👤 {row.get('Nombre', 'N/A')} (CC: {row.get('Cédula', 'N/A')})"):
                    c1, c2 = st.columns([1, 2])
                    with c1:
                        url_foto = row.get('Foto', None)
                        if url_foto and str(url_foto) != 'nan':
                            if url_foto.lower().endswith('.pdf'):
                                st.write("📄 Documento PDF guardado")
                                st.link_button("Ver PDF", url_foto)
                            else:
                                st.image(url_foto, use_container_width=True)
                    with c2:
                        st.write(f"**Teléfono:** {row.get('Teléfono', 'N/D')}")
                        st.write(f"**Observaciones:** {row.get('Observaciones', 'N/D')}")
        else:
            st.info("No hay registros.")
    except Exception as e:
        st.error(f"Error de conexión: {e}")

elif menu == "Agenda de Citas":
    st.header("📅 Agenda")
    st.info("Módulo en desarrollo.")

elif menu == "Configuración":
    st.header("⚙️ Configuración")
    st.write("**Formatos aceptados:** JPG, PNG, JFIF, WEBP, HEIC, PDF, entre otros.")
    # ---------------------------------------------------------
# MÓDULO 3: AGENDA DE CITAS (Actualizado)
# ---------------------------------------------------------
elif menu == "Agenda de Citas":
    st.header("📅 Agenda de Citas")
    
    # 1. Cargamos pacientes para el selector
    try:
        df_pacientes = conn.read(worksheet="Pacientes", ttl=0)
        lista_pacientes = df_pacientes['Nombre'].tolist() if not df_pacientes.empty else []
    except:
        lista_pacientes = []

    tab1, tab2 = st.tabs(["➕ Agendar Nueva", "📋 Ver Agenda"])

    with tab1:
        with st.form("form_cita"):
            col_c1, col_c2 = st.columns(2)
            with col_c1:
                # El usuario elige de la lista de pacientes ya registrados
                paciente_sel = st.selectbox("Seleccionar Paciente", lista_pacientes)
                fecha_cita = st.date_input("Fecha de la Cita", min_value=datetime.date.today())
            with col_c2:
                hora_cita = st.time_input("Hora de la Cita", value=datetime.time(8, 0))
                procedimiento = st.selectbox("Procedimiento", ["Valoración", "Limpieza", "Extracción", "Resina", "Ortodoncia", "Otro"])
            
            notas_cita = st.text_area("Notas adicionales")
            
            if st.form_submit_button("Agendar Cita"):
                if paciente_sel:
                    # Buscamos la cédula del paciente seleccionado
                    cedula_sel = df_pacientes[df_pacientes['Nombre'] == paciente_sel]['Cédula'].values[0]
                    
                    nueva_cita = pd.DataFrame([{
                        "Paciente": paciente_sel,
                        "Cédula": str(cedula_sel),
                        "Fecha": str(fecha_cita),
                        "Hora": str(hora_cita),
                        "Procedimiento": procedimiento,
                        "Observaciones": notas_cita,
                        "Estado": "PENDIENTE"
                    }])
                    
                    conn.update(worksheet="Citas", data=nueva_cita)
                    st.success(f"✅ Cita agendada para {paciente_sel} el {fecha_cita}")
                else:
                    st.error("Primero debe registrar al paciente en el módulo de Registro.")

    with tab2:
        st.subheader("Citas Programadas")
        try:
            df_citas = conn.read(worksheet="Citas", ttl=0)
            if not df_citas.empty:
                # Mostramos la tabla de citas
                st.dataframe(df_citas, use_container_width=True)
            else:
                st.info("No hay citas programadas.")
        except:
            st.warning("Cree la pestaña 'Citas' en su Google Sheets para ver la agenda.")

