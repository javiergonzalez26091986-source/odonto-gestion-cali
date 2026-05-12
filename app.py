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

# --- ESTILOS CSS PERSONALIZADOS (Botones y estética) ---
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
    st.caption("v1.9 - Gestión Profesional")

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
        
        foto = st.file_uploader("Foto Inicial / Rx / Documentos", 
                                type=['jpg', 'png', 'jpeg', 'jfif', 'webp', 'bmp', 'heic', 'pdf'])
        observaciones = st.text_area("Observaciones Iniciales")
        
        if st.form_submit_button("Guardar Paciente"):
            if nombre and cedula and foto:
                with st.spinner("Guardando..."):
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
                        st.success(f"✅ Paciente {nombre} guardado.")
            else:
                st.warning("Complete Nombre, Cédula y Foto.")

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
                        url_foto = row.get('Foto')
                        if url_foto:
                            st.image(url_foto, use_container_width=True)
                    with c2:
                        st.write(f"**Teléfono:** {row.get('Teléfono', 'N/D')}")
                        st.write(f"**Observaciones:** {row.get('Observaciones', 'N/D')}")
        else:
            st.info("No hay pacientes registrados.")
    except:
        st.error("Error al leer la tabla de Pacientes.")

# ---------------------------------------------------------
# MÓDULO 3: AGENDA DE CITAS (Nueva lógica corregida)
# ---------------------------------------------------------
elif menu == "Agenda de Citas":
    st.header("📅 Agenda de Citas")
    
    # Intentar obtener lista de pacientes para el buscador
    try:
        df_p = conn.read(worksheet="Pacientes", ttl=0)
        lista_nombres = df_p['Nombre'].tolist() if not df_p.empty else []
    except:
        lista_nombres = []

    t1, t2 = st.tabs(["➕ Agendar", "📋 Ver Citas"])

    with t1:
        with st.form("nueva_cita"):
            p_nombre = st.selectbox("Seleccione Paciente", options=lista_nombres)
            f_cita = st.date_input("Fecha", min_value=datetime.date.today())
            h_cita = st.time_input("Hora", value=datetime.time(8, 0))
            proc = st.selectbox("Procedimiento", ["Valoración", "Limpieza", "Extracción", "Tratamiento", "Otro"])
            obs_c = st.text_area("Notas")
            
            if st.form_submit_button("Confirmar Cita"):
                if p_nombre:
                    # Traemos la cédula automáticamente
                    p_cedula = df_p[df_p['Nombre'] == p_nombre]['Cédula'].values[0]
                    df_cita = pd.DataFrame([{
                        "Paciente": p_nombre,
                        "Cédula": str(p_cedula),
                        "Fecha": str(f_cita),
                        "Hora": str(h_cita),
                        "Procedimiento": proc,
                        "Observaciones": obs_c,
                        "Estado": "PENDIENTE"
                    }])
                    conn.update(worksheet="Citas", data=df_cita)
                    st.success(f"Cita agendada para {p_nombre}")
                else:
                    st.error("Debe seleccionar un paciente registrado.")

    with t2:
        try:
            df_c = conn.read(worksheet="Citas", ttl=0)
            if not df_c.empty:
                st.dataframe(df_c, use_container_width=True)
            else:
                st.info("No hay citas en la agenda.")
        except:
            st.warning("Asegúrese de que exista la pestaña 'Citas' en su Excel.")

# ---------------------------------------------------------
# MÓDULO 4: CONFIGURACIÓN
# ---------------------------------------------------------
elif menu == "Configuración":
    st.header("⚙️ Configuración")
    st.write("Sistemas operativos.")
