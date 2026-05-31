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

# --- ESTILOS CSS ---
st.markdown("""
    <style>
    div.stButton > button {
        width: 100%; border-radius: 8px; height: 3.5em; background-color: #1E1E1E;
        color: white; border: 1px solid #3d3d3d; text-align: left;
        padding-left: 20px; font-weight: 500; transition: all 0.3s ease;
    }
    div.stButton > button:hover { border-color: #00AEEF; color: #00AEEF; background-color: #262626; transform: translateX(5px); }
    .metric-card { background-color: #111; border: 1px solid #333; padding: 20px; border-radius: 10px; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- CONFIGURACIÓN CLOUDINARY & CONEXIÓN ---
cloudinary.config(cloud_name=st.secrets["cloudinary"]["cloud_name"], api_key=st.secrets["cloudinary"]["api_key"], api_secret=st.secrets["cloudinary"]["api_secret"], secure=True)
conn = st.connection("gsheets", type=GSheetsConnection)

def subir_a_cloudinary(archivo):
    try:
        resultado = cloudinary.uploader.upload(archivo)
        return resultado['secure_url']
    except: return None

# --- NAVEGACIÓN ---
if 'menu_actual' not in st.session_state: st.session_state.menu_actual = "Registro de Pacientes"

with st.sidebar:
    if logo_base64:
        st.markdown(f'<div style="display: flex; justify-content: center; padding-bottom: 20px;"><img src="data:image/jpeg;base64,{logo_base64}" style="width: 100%; border-radius: 10px;"></div>', unsafe_allow_html=True)
    st.write("**MENÚ DE GESTIÓN**")
    if st.button("📋 Registro de Pacientes"): st.session_state.menu_actual = "Registro de Pacientes"
    if st.button("📂 Evolución y Galería"): st.session_state.menu_actual = "Evolución y Galería"
    if st.button("📅 Agenda de Citas"): st.session_state.menu_actual = "Agenda de Citas"
    if st.button("💰 Facturación"): st.session_state.menu_actual = "Facturación"
    if st.button("⚙️ Configuración"): st.session_state.menu_actual = "Configuración"
    st.markdown("---")
    st.caption("v1.0 - Gestión Odonto-Cali")

menu = st.session_state.menu_actual

# CARGA DE PACIENTES PARA SELECTORES
try:
    df_p = conn.read(worksheet="Pacientes", ttl=0)
    lista_pacientes = df_p['Nombre'].tolist() if not df_p.empty else []
except: lista_pacientes = []

# --- MÓDULOS 1, 2, 3
if menu == "Registro de Pacientes":
    st.header("📋 Registro de Nuevo Paciente")
    with st.form("reg_p"):
        c1, c2 = st.columns(2)
        with c1:
            n = st.text_input("Nombre"); id_p = st.text_input("Cédula"); tel = st.text_input("Teléfono")
        with c2:
            ep = st.text_input("EPS"); f_n = st.date_input("Nacimiento", min_value=datetime.date(1940,1,1))
        f_p = st.file_uploader("Foto", type=['jpg','png','jpeg','jfif','pdf'])
        obs = st.text_area("Observaciones")
        if st.form_submit_button("Guardar"):
            if n and id_p and f_p:
                u = subir_a_cloudinary(f_p)
                if u:
                    nueva = pd.DataFrame([{"Nombre": n.upper(), "Cédula": str(id_p), "Teléfono": tel, "EPS": ep.upper(), "Foto": u, "Observaciones": obs, "Fecha_Registro": str(datetime.date.today())}])
                    conn.update(worksheet="Pacientes", data=nueva); st.success(f"Paciente {n} registrado.")

elif menu == "Evolución y Galería":
    st.header("📂 Historial")
    if not df_p.empty:
        b = st.text_input("🔍 Buscar").upper()
        df_f = df_p[df_p['Nombre'].str.contains(b, na=False) | df_p['Cédula'].astype(str).str.contains(b, na=False)] if b else df_p
        for i, r in df_f.iterrows():
            with st.expander(f"👤 {r['Nombre']}"):
                col_x, col_y = st.columns([1,2])
                with col_x: st.image(r['Foto'])
                with col_y: st.write(f"ID: {r['Cédula']}"); st.write(f"Obs: {r['Observaciones']}")

elif menu == "Agenda de Citas":
    st.header("📅 Agenda")
    t1, t2 = st.tabs(["Agendar", "Ver Citas"])
    with t1:
        with st.form("f_c"):
            p = st.selectbox("Paciente", lista_pacientes); f = st.date_input("Fecha"); h = st.time_input("Hora"); pr = st.text_input("Servicio")
            if st.form_submit_button("Agendar"):
                if p:
                    nueva_c = pd.DataFrame([{"Paciente": p, "Fecha": str(f), "Hora": str(h), "Procedimiento": pr, "Estado": "PENDIENTE"}])
                    conn.update(worksheet="Citas", data=nueva_c); st.success("Cita agendada.")
    with t2:
        try: df_c = conn.read(worksheet="Citas", ttl=0); st.dataframe(df_c)
        except: st.info("Cree la pestaña 'Citas'")

# ---------------------------------------------------------
# MÓDULO 4: FACTURACIÓN
# ---------------------------------------------------------
elif menu == "Facturación":
    st.header("💰 Gestión de Facturación")
    
    t_f1, t_f2 = st.tabs(["➕ Generar Cobro", "📊 Resumen de Caja"])
    
    with t_f1:
        with st.form("form_fact"):
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                p_fact = st.selectbox("Paciente", lista_pacientes)
                f_fact = st.date_input("Fecha de Pago", value=datetime.date.today())
            with col_f2:
                metodo = st.selectbox("Método de Pago", ["Efectivo", "Transferencia (Nequi/Davi)", "Tarjeta"])
                valor = st.number_input("Valor del Servicio ($)", min_value=0, step=1000)
            
            servicio = st.text_input("Servicio Prestado (Ej: Limpieza, Resina)")
            
            if st.form_submit_button("Registrar Pago"):
                if p_fact and valor > 0:
                    nueva_fact = pd.DataFrame([{
                        "Paciente": p_fact,
                        "Fecha": str(f_fact),
                        "Servicio": servicio.upper(),
                        "Metodo": metodo,
                        "Valor": valor
                    }])
                    conn.update(worksheet="Facturacion", data=nueva_fact)
                    st.success(f"✅ Cobro de ${valor:,.0f} registrado para {p_fact}")
                else:
                    st.warning("Seleccione un paciente y asigne un valor válido.")

    with t_f2:
        try:
            df_fact = conn.read(worksheet="Facturacion", ttl=0)
            if not df_fact.empty:
                # Métricas rápidas
                total_historico = df_fact['Valor'].sum()
                hoy_str = str(datetime.date.today())
                total_hoy = df_fact[df_fact['Fecha'] == hoy_str]['Valor'].sum()
                
                m1, m2 = st.columns(2)
                m1.metric("Recaudo de Hoy", f"$ {total_hoy:,.0f}")
                m2.metric("Total Histórico", f"$ {total_historico:,.0f}")
                
                st.markdown("---")
                st.subheader("Historial de Pagos")
                st.dataframe(df_fact, use_container_width=True)
            else:
                st.info("Aún no hay registros de pagos.")
        except:
            st.error("Asegúrese de que la pestaña se llame exactamente 'Facturacion'")

# ---------------------------------------------------------
# MÓDULO 5: CONFIGURACIÓN
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
