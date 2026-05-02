import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime
from PIL import Image

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Gestión Odontológica", page_icon="🦷")
st.title("🦷 Gestión - Odontología Familiar Especializada")

# URL de la carpeta de Drive proporcionada por el usuario
URL_CARPETA_DRIVE = "https://drive.google.com/drive/folders/1hauuaIMZOztMBJSUANg0Ce7kquOAqYEu"

# Conexión a Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Lectura de datos existentes (ttl=0 para datos frescos)
df_pacientes = conn.read(worksheet="Pacientes", ttl=0)

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
        foto_perfil = st.file_uploader("Subir foto inicial / Perfil", type=['jpg', 'png', 'jpeg'])
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
                # Actualización de la hoja Pacientes
                conn.update(worksheet="Pacientes", data=nuevo_paciente)
                st.success(f"¡Paciente {nombre} registrado con éxito!")
                if foto_perfil:
                    st.info(f"Foto recibida. Recuerda subirla manualmente a la carpeta de Drive si es necesario: {URL_CARPETA_DRIVE}")
                st.cache_data.clear()
            else:
                st.error("Nombre y Cédula son obligatorios.")

# --- MÓDULO 2: EVOLUCIÓN DE PACIENTES ---
elif menu == "Evolución de Pacientes":
    st.header("📝 Evolución y Consultas")
    
    if not df_pacientes.empty:
        nombres_pacientes = df_pacientes['Nombre'].unique().tolist()
        seleccion = st.selectbox("Seleccione el Paciente", [""] + nombres_pacientes)
        
        if seleccion != "":
            datos_p = df_pacientes[df_pacientes['Nombre'] == seleccion].iloc[0]
            st.info(f"Paciente: **{seleccion}** | CC: **{datos_p['Cédula']}**")
            
            with st.form("form_consulta"):
                f_consulta = st.date_input("Fecha", datetime.date.today())
                motivo = st.text_area("Motivo de Consulta")
                diagnostico = st.text_area("Diagnóstico")
                tratamiento = st.text_area("Tratamiento")
                archivo_foto = st.file_uploader("Subir Radiografía / Foto del día", type=['jpg', 'png', 'jpeg'])
                
                if st.form_submit_button("Guardar Consulta"):
                    nueva_consulta = pd.DataFrame([{
                        "Cédula": str(datos_p['Cédula']),
                        "Fecha": str(f_consulta),
                        "Motivo": motivo.upper(),
                        "Diagnóstico": diagnostico.upper(),
                        "Tratamiento": tratamiento.upper(),
                        "Link_Foto": URL_CARPETA_DRIVE if archivo_foto else "SIN FOTO"
                    }])
                    # Actualización de la hoja Consultas
                    conn.update(worksheet="Consultas", data=nueva_consulta)
                    st.success("Consulta guardada exitosamente.")
                    if archivo_foto:
                        st.image(archivo_foto, caption="Vista previa de la imagen cargada")
                    st.cache_data.clear()
    else:
        st.error("No hay pacientes registrados.")

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
                # Actualización de la hoja Facturacion
                conn.update(worksheet="Facturacion", data=nueva_factura)
                st.success("Pago registrado exitosamente")
                st.cache_data.clear()
