import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Gestión Odontológica", page_icon="🦷")
st.title("🦷 Gestión - Odontología Familiar Especializada")

# URL de tu carpeta de Drive para acceso rápido
URL_CARPETA_DRIVE = "https://drive.google.com/drive/folders/1hauuaIMZOztMBJSUANg0Ce7kquOAqYEu"

# --- CONEXIÓN A SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

# Intentar leer los datos existentes para que el resto de los módulos funcionen
try:
    df_pacientes = conn.read(worksheet="Pacientes", ttl=0)
except Exception:
    df_pacientes = pd.DataFrame()

menu = st.sidebar.selectbox("Seleccione una opción", ["Registro de Pacientes", "Evolución de Pacientes", "Facturacion Interna"])

# --- MÓDULO 1: REGISTRO DE PACIENTES ---
if menu == "Registro de Pacientes":
    st.header("📋 Registro de Nuevo Paciente")
    with st.form("form_reg"):
        nombre = st.text_input("Nombre Completo")
        cedula = st.text_input("Cédula")
        tel = st.text_input("Teléfono")
        fecha_reg = st.date_input("Fecha de Registro", datetime.date.today())
        nota = st.text_area("Notas")
        
        st.info(f"📂 Nota: Sube las fotos directamente a la carpeta de Drive: [Abrir Carpeta]({URL_CARPETA_DRIVE})")
        
        if st.form_submit_button("Registrar Paciente"):
            if nombre and cedula:
                nuevo = pd.DataFrame([{
                    "Nombre": nombre.upper(), 
                    "Cédula": str(cedula), 
                    "Teléfono": str(tel), 
                    "Fecha": str(fecha_reg), 
                    "Notas": nota.upper(),
                    "Foto": "VER EN DRIVE"
                }])
                
                conn.update(worksheet="Pacientes", data=nuevo)
                st.success(f"✅ Paciente {nombre} registrado con éxito.")
                st.cache_data.clear()
            else:
                st.error("Nombre y Cédula son obligatorios.")

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
                
                if st.form_submit_button("Guardar Evolución"):
                    nueva_ev = pd.DataFrame([{
                        "Cédula": str(cedula_p),
                        "Fecha": str(f_ev),
                        "Motivo": motivo.upper(),
                        "Diagnóstico": diag.upper(),
                        "Tratamiento": trata.upper(),
                        "Link_Foto": "VER EN DRIVE"
                    }])
                    conn.update(worksheet="Consultas", data=nueva_ev)
                    st.success("✅ Evolución guardada correctamente.")
                    st.cache_data.clear()
    else:
        st.warning("No hay pacientes registrados aún.")

# --- MÓDULO 3: FACTURACIÓN ---
elif menu == "Facturacion Interna":
    st.header("💰 Facturación")
    if not df_pacientes.empty:
        p_f = st.selectbox("Paciente", df_pacientes['Nombre'].unique().tolist())
        with st.form("f_pago"):
            serv = st.text_input("Servicio")
            val = st.number_input("Valor", min_value=0)
            if st.form_submit_button("Registrar Pago"):
                pago = pd.DataFrame([{
                    "Paciente": p_f, 
                    "Fecha": str(datetime.date.today()), 
                    "Servicio": serv.upper(), 
                    "Valor": val
                }])
                conn.update(worksheet="Facturacion", data=pago)
                st.success("✅ Pago registrado.")
                st.cache_data.clear()
