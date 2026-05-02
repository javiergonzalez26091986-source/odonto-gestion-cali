import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime

# Configuración de la página
st.set_page_config(page_title="Gestión Odontológica", page_icon="🦷")

st.title("🦷 Gestión - Odontología Familiar Especializada")

# Conexión a Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Lectura de datos existentes
df_pacientes = conn.read(worksheet="Pacientes")

# Menú Lateral
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
                conn.create(worksheet="Pacientes", data=nuevo_paciente)
                st.success(f"¡Paciente {nombre} registrado con éxito!")
                st.cache_data.clear()
            else:
                st.error("Nombre y Cédula son obligatorios.")

# --- MÓDULO 2: EVOLUCIÓN DE PACIENTES (EL NUEVO) ---
elif menu == "Evolución de Pacientes":
    st.header("📝 Evolución y Consultas")
    
    if not df_pacientes.empty:
        # Buscador por nombre
        nombres_lista = df_pacientes['Nombre'].tolist()
        seleccion_nombre = st.selectbox("Seleccione el Paciente", [""] + nombres_lista)
        
        if seleccion_nombre != "":
            # Obtener la cédula del paciente seleccionado
            datos_paciente = df_pacientes[df_pacientes['Nombre'] == seleccion_nombre]
            cedula_sel = datos_paciente['Cédula'].values[0]
            
            st.info(f"Registrando consulta para: **{seleccion_nombre}** (CC: {cedula_sel})")
            
            with st.form("form_consulta"):
                f_consulta = st.date_input("Fecha de Consulta", datetime.date.today())
                motivo = st.text_area("Motivo de la Consulta")
                diagnostico = st.text_area("Diagnóstico / Hallazgos")
                tratamiento = st.text_area("Tratamiento Realizado / Plan")
                
                if st.form_submit_button("Guardar Evolución"):
                    nueva_fila_consulta = pd.DataFrame([{
                        "Cédula": str(cedula_sel),
                        "Fecha": str(f_consulta),
                        "Motivo": motivo.upper(),
                        "Diagnóstico": diagnostico.upper(),
                        "Tratamiento": tratamiento.upper(),
                        "Link_Foto": ""
                    }])
                    
                    # Guardar en la pestaña Consultas
                    conn.create(worksheet="Consultas", data=nueva_fila_consulta)
                    st.success("¡Evolución guardada correctamente en la ficha del paciente!")
                    st.cache_data.clear()
    else:
        st.warning("No hay pacientes registrados para crear una evolución.")

# --- MÓDULO 3: FACTURACIÓN INTERNA ---
elif menu == "Facturacion Interna":
    st.header("💰 Registro de Facturación")
    if not df_pacientes.empty:
        nombres_lista = df_pacientes['Nombre'].tolist()
        paciente_fact = st.selectbox("Paciente a Facturar", nombres_lista)
        
        with st.form("form_factura"):
            servicio = st.text_input("Concepto / Servicio")
            valor = st.number_input("Valor total", min_value=0)
            metodo = st.selectbox("Método de Pago", ["Efectivo", "Transferencia", "Tarjeta"])
            
            if st.form_submit_button("Registrar Pago"):
                nueva_factura = pd.DataFrame([{
                    "Paciente": paciente_fact,
                    "Fecha": str(datetime.date.today()),
                    "Servicio": servicio.upper(),
                    "Valor": valor,
                    "Metodo": metodo
                }])
                conn.create(worksheet="Facturacion", data=nueva_factura)
                st.success("¡Factura registrada!")
                st.cache_data.clear()
