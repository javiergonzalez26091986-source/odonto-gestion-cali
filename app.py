import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime

# 1. Configuración y Conexión (Lo que ya funcionaba)
st.set_page_config(page_title="Gestión Odontológica", page_icon="🦷")
st.title("🦷 Gestión - Odontología Familiar Especializada")

conn = st.connection("gsheets", type=GSheetsConnection)

# 2. Carga de datos CRÍTICA (Para que aparezcan los pacientes en la lista)
df_pacientes = conn.read(worksheet="Pacientes", ttl=0)

# Menú Lateral con la estructura limpia
menu = st.sidebar.selectbox(
    "Seleccione una opción", 
    ["Registro de Pacientes", "Evolución de Pacientes", "Facturacion Interna"]
)

# --- MÓDULO 1: REGISTRO DE PACIENTES ---
if menu == "Registro de Pacientes":
    st.header("📋 Registro de Nuevo Paciente")
    with st.form("form_registro"):
        nombre = st.text_input("Nombre Completo")
        cedula = st.text_input("Cédula")
        telefono = st.text_input("Teléfono")
        fecha = st.date_input("Fecha de Registro", datetime.date.today())
        notas = st.text_area("Notas Iniciales")
        
        if st.form_submit_button("Registrar Paciente"):
            if nombre and cedula:
                nuevo_paciente = pd.DataFrame([{
                    "Nombre": nombre.upper(),
                    "Cédula": str(cedula),
                    "Teléfono": str(telefono),
                    "Fecha": str(fecha),
                    "Notas": notas.upper()
                }])
                # Usamos update para no borrar los encabezados
                conn.update(worksheet="Pacientes", data=nuevo_paciente)
                st.success(f"¡Paciente {nombre} registrado con éxito!")
                st.cache_data.clear()
            else:
                st.error("Nombre y Cédula son obligatorios.")

# --- MÓDULO 2: EVOLUCIÓN DE PACIENTES (Corregido para leer el Sheets) ---
elif menu == "Evolución de Pacientes":
    st.header("📝 Evolución y Consultas")
    
    if not df_pacientes.empty:
        # Aquí cargamos los nombres reales de tu Google Sheets
        nombres_pacientes = df_pacientes['Nombre'].unique().tolist()
        seleccion = st.selectbox("Seleccione el Paciente para registrar consulta", [""] + nombres_pacientes)
        
        if seleccion != "":
            # Extraemos la cédula del paciente elegido
            datos_p = df_pacientes[df_pacientes['Nombre'] == seleccion].iloc[0]
            st.info(f"Paciente: **{seleccion}** | CC: **{datos_p['Cédula']}**")
            
            with st.form("form_consulta"):
                f_consulta = st.date_input("Fecha", datetime.date.today())
                motivo = st.text_area("Motivo de Consulta")
                diagnostico = st.text_area("Diagnóstico")
                tratamiento = st.text_area("Tratamiento")
                
                if st.form_submit_button("Guardar Consulta"):
                    nueva_consulta = pd.DataFrame([{
                        "Cédula": str(datos_p['Cédula']),
                        "Fecha": str(f_consulta),
                        "Motivo": motivo.upper(),
                        "Diagnóstico": diagnostico.upper(),
                        "Tratamiento": tratamiento.upper(),
                        "Link_Foto": ""
                    }])
                    conn.update(worksheet="Consultas", data=nueva_consulta)
                    st.success("Consulta guardada en la pestaña Consultas")
                    st.cache_data.clear()
    else:
        st.error("No se encontraron datos en la pestaña 'Pacientes'. Verifica el Google Sheets.")

# --- MÓDULO 3: FACTURACIÓN INTERNA ---
elif menu == "Facturacion Interna":
    st.header("💰 Registro de Facturación")
    if not df_pacientes.empty:
        nombres_f = df_pacientes['Nombre'].unique().tolist()
        p_fact = st.selectbox("Paciente a Facturar", nombres_f)
        
        with st.form("form_factura"):
            servicio = st.text_input("Concepto")
            valor = st.number_input("Valor", min_value=0)
            
            if st.form_submit_button("Registrar Pago"):
                nueva_factura = pd.DataFrame([{
                    "Paciente": p_fact,
                    "Fecha": str(datetime.date.today()),
                    "Servicio": servicio.upper(),
                    "Valor": valor
                }])
                conn.update(worksheet="Facturacion", data=nueva_factura)
                st.success("Pago registrado exitosamente")
                st.cache_data.clear()
