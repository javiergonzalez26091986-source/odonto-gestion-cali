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

# Leer datos existentes para los selectores
try:
    df_pacientes = conn.read(worksheet="Pacientes", ttl=0)
except Exception:
    df_pacientes = pd.DataFrame(columns=["Nombre", "Cédula", "Teléfono", "Fecha", "Notas", "Foto"])

menu = st.sidebar.selectbox("Seleccione una opción", ["Registro de Pacientes", "Evolución de Pacientes", "Facturacion Interna"])

# --- MÓDULO 1: REGISTRO DE PACIENTES ---
if menu == "Registro de Pacientes":
    st.header("📋 Registro de Nuevo Paciente")
    
    with st.form("form_registro_paciente", clear_on_submit=True):
        nombre = st.text_input("Nombre Completo")
        cedula = st.text_input("Cédula / Identificación")
        tel = st.text_input("Teléfono de Contacto")
        fecha_reg = st.date_input("Fecha de Registro", datetime.date.today())
        nota = st.text_area("Notas iniciales / Antecedentes")
        
        st.info(f"📂 Recuerda subir la foto del paciente a Drive con su número de cédula: [Abrir Carpeta]({URL_CARPETA_DRIVE})")
        
        enviar = st.form_submit_button("Registrar Paciente")
        
        if enviar:
            if nombre.strip() != "" and cedula.strip() != "":
                # Creamos el DataFrame con la estructura exacta de tu Excel
                nuevo_registro = pd.DataFrame([{
                    "Nombre": nombre.upper(), 
                    "Cédula": str(cedula), 
                    "Teléfono": str(tel), 
                    "Fecha": str(fecha_reg), 
                    "Notas": nota.upper(),
                    "Foto": "VER EN DRIVE"
                }])
                
                # Enviamos a Google Sheets
                try:
                    conn.update(worksheet="Pacientes", data=nuevo_registro)
                    st.success(f"✅ Paciente {nombre.upper()} registrado exitosamente.")
                    st.cache_data.clear() # Limpiar caché para que aparezca en Evolución
                except Exception as e:
                    st.error(f"Error al guardar en Google Sheets: {e}")
            else:
                st.warning("⚠️ El nombre y la cédula son obligatorios para el registro.")

# --- MÓDULO 2: EVOLUCIÓN DE PACIENTES (Historial) ---
elif menu == "Evolución de Pacientes":
    st.header("📝 Evolución y Consultas")
    if not df_pacientes.empty:
        # Filtrar nombres vacíos
        nombres_validos = df_pacientes['Nombre'].dropna().unique().tolist()
        paciente_sel = st.selectbox("Seleccione el Paciente", [""] + nombres_validos)
        
        if paciente_sel != "":
            cedula_p = df_pacientes[df_pacientes['Nombre'] == paciente_sel]['Cédula'].values[0]
            st.subheader(f"Paciente: {paciente_sel} (CC: {cedula_p})")
            
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
                    st.success("✅ Evolución guardada.")
                    st.cache_data.clear()
    else:
        st.warning("No hay pacientes registrados en la base de datos.")

# --- MÓDULO 3: FACTURACIÓN ---
elif menu == "Facturacion Interna":
    st.header("💰 Facturación")
    if not df_pacientes.empty:
        p_f = st.selectbox("Paciente", df_pacientes['Nombre'].dropna().unique().tolist())
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
