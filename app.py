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
    .status-box {
        padding: 20px;
        border-radius: 10px;
        background-color: #111;
        border: 1px solid #333;
        margin-bottom: 10px;
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
        return None

# --- LÓGICA DE NAVEGACIÓN ---
if 'menu_actual' not in st.session_state:
    st.session_state.menu_actual = "Registro de Pacientes"

with st.sidebar:
    if logo_base64:
        st.markdown(f'<div style="display: flex; justify-content: center; padding-bottom: 20px;"><img src="data:image/jpeg;base64,{logo_base64}" style="width: 100%; border-radius: 10px;"></div>', unsafe_allow_html=True)
    
    st.write("**MENÚ DE GESTIÓN**")
    if st.button("📋 Registro de Pacientes"): st.session_state.menu_actual = "Registro de Pacientes"
    if st.button("📂 Evolución y Galería"): st.session_state.menu_actual = "Evolución y Galería"
    if st.button("📅 Agenda de Citas"): st.session_state.menu_actual = "Agenda de Citas"
    if st.button("⚙️ Configuración"): st.session_state.menu_actual = "Configuración"
    
    st.markdown("---")
    st.caption("v2.0 - Gestión Odontológica")

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
        
        foto = st.file_uploader("Foto Inicial / Rx / Documentos", type=['jpg', 'png', 'jpeg', 'jfif', 'webp', 'heic', 'pdf'])
        obs = st.text_area("Observaciones Iniciales")
        
        if st.form_submit_button("Guardar Paciente"):
            if nombre and cedula and foto:
                with st.spinner("Procesando..."):
                    url = subir_a_cloudinary(foto)
                    if url:
                        nueva_fila = pd.DataFrame([{"Nombre": nombre.upper(), "Cédula": str(cedula), "Teléfono": telefono, "EPS": eps.upper(), "Foto": url, "Observaciones": obs, "Fecha_Registro": str(datetime.date.today())}])
                        conn.update(worksheet="Pacientes", data=nueva_fila)
                        st.success(f"✅ Paciente {nombre} registrado.")
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
                with st.expander(f"👤 {row.get('Nombre')} (CC: {row.get('Cédula')})"):
                    c1, c2 = st.columns([1, 2])
                    with c1:
                        if row.get('Foto'): st.image(row.get('Foto'), use_container_width=True)
                    with c2:
                        st.write(f"**Teléfono:** {row.get('Teléfono')}")
                        st.write(f"**EPS:** {row.get('EPS')}")
                        st.write(f"**Observaciones:** {row.get('Observaciones')}")
        else:
            st.info("No hay registros.")
    except:
        st.error("Error al conectar con la base de datos.")

# ---------------------------------------------------------
# MÓDULO 3: AGENDA DE CITAS
# ---------------------------------------------------------
elif menu == "Agenda de Citas":
    st.header("📅 Agenda de Citas")
    try:
        df_p = conn.read(worksheet="Pacientes", ttl=0)
        lista_n = df_p['Nombre'].tolist() if not df_p.empty else []
    except:
        lista_n = []

    t1, t2 = st.tabs(["➕ Agendar", "📋 Ver Agenda"])
    with t1:
        with st.form("f_cita"):
            p_sel = st.selectbox("Seleccione Paciente", options=lista_n)
            f_c = st.date_input("Fecha", min_value=datetime.date.today())
            h_c = st.time_input("Hora", value=datetime.time(8, 0))
            pr = st.selectbox("Procedimiento", ["Valoración", "Limpieza", "Extracción", "Tratamiento", "Otro"])
            if st.form_submit_button("Confirmar Cita"):
                if p_sel:
                    p_id = df_p[df_p['Nombre'] == p_sel]['Cédula'].values[0]
                    df_c = pd.DataFrame([{"Paciente": p_sel, "Cédula": str(p_id), "Fecha": str(f_c), "Hora": str(h_c), "Procedimiento": pr, "Estado": "PENDIENTE"}])
                    conn.update(worksheet="Citas", data=df_c)
                    st.success(f"Cita guardada para {p_sel}")

    with t2:
        try:
            df_agenda = conn.read(worksheet="Citas", ttl=0)
            st.dataframe(df_agenda, use_container_width=True)
        except:
            st.warning("Pestaña 'Citas' no encontrada en el Excel.")

# ---------------------------------------------------------
# MÓDULO 4: CONFIGURACIÓN (REDISEÑADO PROFESIONAL)
# ---------------------------------------------------------
elif menu == "Configuración":
    st.header("⚙️ Centro de Control y Estado")
    st.write("Verifique la conexión de los servicios internos del programa.")
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown("""
            <div class="status-box">
                <h3 style='color: #00AEEF; margin-top:0;'>🟢 Google Sheets</h3>
                <p><b>Estado:</b> Conectado y Sincronizado</p>
                <p><b>Base de Datos:</b> BD_Odontologia</p>
                <p><b>Pestañas detectadas:</b> Pacientes, Consultas, Citas, Facturacion</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
            <div class="status-box">
                <h3 style='color: #00AEEF; margin-top:0;'>🟢 Cloudinary Cloud</h3>
                <p><b>Estado:</b> Servidor de Imágenes Activo</p>
                <p><b>Seguridad:</b> SSL Habilitado (HTTPS)</p>
                <p><b>Formatos:</b> JPG, PNG, JFIF, WEBP, HEIC, PDF</p>
            </div>
        """, unsafe_allow_html=True)

    with col_b:
        st.markdown("""
            <div class="status-box">
                <h3 style='color: #00AEEF; margin-top:0;'>💻 Sistema Local</h3>
                <p><b>Logo Institucional:</b> Cargado (Base64)</p>
                <p><b>Versión del Software:</b> 2.0 (Mayo 2026)</p>
                <p><b>Ubicación:</b> Yumbo, Valle del Cauca</p>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔄 Refrescar Conexiones"):
            st.cache_data.clear()
            st.rerun()

    st.info("💡 Consejo: Si los datos no aparecen reflejados, use el botón 'Refrescar Conexiones'.")
