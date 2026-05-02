import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime
import requests

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Gestión Odontológica", page_icon="🦷", layout="wide")
st.title("🦷 Gestión - Odontología Familiar Especializada")

# ID de tu carpeta de fotos (extraído de tu URL)
ID_CARPETA_DRIVE = "1hauuaIMZOztMBJSUANg0Ce7kquOAqYEu"

# --- CONEXIÓN A SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    df_pacientes = conn.read(worksheet="Pacientes", ttl=0)
except Exception:
    df_pacientes = pd.DataFrame(columns=["Nombre", "Cédula", "Teléfono", "Fecha", "Notas", "Foto"])

# --- FUNCIÓN PARA MOSTRAR FOTOS DIRECTAMENTE ---
def visor_imagenes_drive(cedula):
    st.markdown(f"### 📸 Galería Clínica (CC: {cedula})")
    # Nota: Para visualización directa sin API de Google, usamos el buscador de miniaturas
    # Esto funciona si las imágenes están en la carpeta y son públicas o accesibles al navegador
    
    # Intentamos cargar una imagen de ejemplo basada en el patrón de nombre: CEDULA_1.jpg
    # Como no sabemos el nombre exacto de cada archivo, lo ideal es usar el link directo
    st.info("Para ver las fotos aquí, asegúrate de nombrarlas solo con la cédula (ej: 1130629192.jpg)")
    
    # Generamos el link de visualización directa
    # Intentamos mostrar la imagen principal del paciente
    url_foto = f"https://drive.google.com/thumbnail?id={ID_CARPETA_DRIVE}&sz=w1000" 
    
    # Como alternativa robusta para mostrar MULTIPLES fotos directamente:
    st.markdown(f'<iframe src="https://drive.google.com/embeddedfolderview?id={ID_CARPETA_DRIVE}#list" width="100%" height="400" frameborder="0"></iframe>', unsafe_allow_html=True)
    st.caption("Arriba puedes ver y abrir las fotos guardadas en la carpeta compartida.")

menu = st.sidebar.selectbox("Seleccione una opción", ["Registro de Pacientes", "Evolución de Pacientes", "Facturacion Interna"])

# --- MÓDULO 1: REGISTRO --- (Se mantiene igual)
if menu == "Registro de Pacientes":
    st.header("📋 Registro de Nuevo Paciente")
    with st.form("form_reg"):
        nombre = st.text_input("Nombre Completo")
        cedula = st.text_input("Cédula")
        tel = st.text_input("Teléfono")
        if st.form_submit_button("Registrar"):
            nuevo = pd.DataFrame([{"Nombre": nombre.upper(), "Cédula": str(cedula), "Teléfono": str(tel), "Fecha": str(datetime.date.today()), "Notas": "", "Foto": "DRIVE"}])
            conn.update(worksheet="Pacientes", data=nuevo)
            st.success("Registrado")
            st.cache_data.clear()

# --- MÓDULO 2: EVOLUCIÓN (CON VISOR DE FOTOS) ---
elif menu == "Evolución de Pacientes":
    st.header("📝 Evolución y Consultas")
    if not df_pacientes.empty:
        nombres_validos = df_pacientes['Nombre'].dropna().unique().tolist()
        paciente_sel = st.selectbox("Seleccione el Paciente", [""] + nombres_validos)
        
        if paciente_sel != "":
            datos_p = df_pacientes[df_pacientes['Nombre'] == paciente_sel].iloc[0]
            cedula_p = str(datos_p['Cédula']).split('.')[0]
            
            # DISEÑO EN COLUMNAS
            col_info, col_fotos = st.columns([1, 1])
            
            with col_info:
                st.subheader(f"📜 Historial: {paciente_sel}")
                try:
                    df_consultas = conn.read(worksheet="Consultas", ttl=0)
                    historial = df_consultas[df_consultas['Cédula'].astype(str).str.contains(cedula_p)]
                    if not historial.empty:
                        for i, fila in historial.iterrows():
                            with st.expander(f"Consulta: {fila['Fecha']}"):
                                st.write(f"**Motivo:** {fila['Motivo']}")
                                st.write(f"**Tratamiento:** {fila['Tratamiento']}")
                    else: st.info("Sin registros.")
                except: st.info("Inicie el registro de consultas.")

            with col_fotos:
                # AQUÍ SE MUESTRAN LAS FOTOS DIRECTAMENTE
                visor_imagenes_drive(cedula_p)

            st.divider()
            st.subheader("Añadir Nueva Evolución")
            with st.form("form_ev"):
                f_ev = st.date_input("Fecha", datetime.date.today())
                motivo = st.text_area("Motivo")
                trata = st.text_area("Tratamiento")
                if st.form_submit_button("Guardar"):
                    nueva_ev = pd.DataFrame([{"Cédula": str(cedula_p), "Fecha": str(f_ev), "Motivo": motivo.upper(), "Diagnóstico": "", "Tratamiento": trata.upper(), "Link_Foto": "DRIVE"}])
                    conn.update(worksheet="Consultas", data=nueva_ev)
                    st.success("Guardado")
                    st.cache_data.clear()

# --- MÓDULO 3: FACTURACIÓN --- (Se mantiene igual)
elif menu == "Facturacion Interna":
    st.header("💰 Facturación")
    # ... (resto del código de facturación)
