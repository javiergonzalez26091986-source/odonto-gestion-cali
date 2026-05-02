import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Gestión Odontológica", page_icon="🦷")
st.title("🦷 Gestión - Odontología Familiar Especializada")

# URL de tu carpeta de Drive
URL_CARPETA_DRIVE = "https://drive.google.com/drive/folders/1hauuaIMZOztMBJSUANg0Ce7kquOAqYEu"

# Conexión
conn = st.connection("gsheets", type=GSheetsConnection)

# Carga de datos (Si esto falla, la app se pone en blanco, por eso lo envolvemos en un try)
try:
    df_pacientes = conn.read(worksheet="Pacientes", ttl=0)
except:
    df_pacientes = pd.DataFrame(columns=["Nombre", "Cédula", "Teléfono", "Fecha", "Notas"])

# Menú
menu = st.sidebar.selectbox(
    "Seleccione una opción", 
    ["Registro de Pacientes", "Evolución de Pacientes", "Facturacion Interna"]
)

# --- MÓDULO 1: REGISTRO DE PACIENTES ---
if menu == "Registro de Pacientes":
    st.header("📋 Registro de Nuevo Paciente")
    with st.form("form_registro", clear_on_submit=True):
        nombre = st.text_input("Nombre Completo")
        cedula = st.text_input("Cédula")
        telefono = st.text_input("Teléfono")
        fecha = st.date_input("Fecha de Registro", datetime.date.today())
        foto_perfil = st.file_uploader("Subir foto inicial / Perfil", type=['jpg', 'png', 'jpeg'])
        notas = st.text_area("Notas Iniciales")
        
        if st.form_submit_button("Registrar Paciente"):
            if nombre and cedula:
                nuevo_p = pd.DataFrame([{
                    "Nombre": nombre.upper(),
                    "Cédula": str(cedula),
                    "Teléfono": str(telefono),
                    "Fecha": str(fecha),
                    "Notas": notas.upper()
                }])
                conn.update(worksheet="Pacientes", data=nuevo_p)
                st.success(f"✅ ¡{nombre} registrado!")
                if foto_perfil:
                    st.info(f"📂 Por favor, sube la foto aquí: {URL_CARPETA_DRIVE}")
                st.cache_data.clear()
            else:
                st.error("Nombre y Cédula son obligatorios.")

# --- MÓDULO 2: EVOLUCIÓN DE PACIENTES ---
elif menu == "Evolución de Pacientes":
    st.header("📝 Evolución y Consultas")
    if not df_pacientes.empty:
        nombres = df_pacientes['Nombre'].unique().tolist()
        sel = st.selectbox("Seleccione el Paciente", [""] + nombres)
        
        if sel != "":
            datos = df_pacientes[df_pacientes['Nombre'] == sel].iloc[0]
            cedula_p = datos['Cédula']
            
            with st.form("form_ev"):
                f_ev = st.date_input("Fecha", datetime.date.today())
                motivo = st.text_area("Motivo")
                diag = st.text_area("Diagnóstico")
                trata = st.text_area("Tratamiento")
                archivo = st.file_uploader("Subir Radiografía", type=['jpg', 'png', 'jpeg'])
                
                if st.form_submit_button("Guardar Evolución"):
                    # El link guardado será el de la carpeta para que el Dr. entre directo
                    nueva_ev = pd.DataFrame([{
                        "Cédula": str(cedula_p),
                        "Fecha": str(f_ev),
                        "Motivo": motivo.upper(),
                        "Diagnóstico": diag.upper(),
                        "Tratamiento": trata.upper(),
                        "Link_Foto": URL_CARPETA_DRIVE if archivo else "SIN FOTO"
                    }])
                    conn.update(worksheet="Consultas", data=nueva_ev)
                    st.success("✅ Evolución guardada.")
                    if archivo:
                        st.warning(f"📸 Recuerda subir la imagen a la carpeta de Drive.")
                    st.cache_data.clear()

# --- MÓDULO 3: FACTURACIÓN ---
elif menu == "Facturacion Interna":
    st.header("💰 Registro de Facturación")
    if not df_pacientes.empty:
        nombres_f = df_pacientes['Nombre'].unique().tolist()
        p_f = st.selectbox("Paciente", nombres_f)
        with st.form("form_pago"):
            serv = st.text_input("Concepto")
            monto = st.number_input("Valor", min_value=0)
            if st.form_submit_button("Guardar Pago"):
                pago = pd.DataFrame([{"Paciente": p_f, "Fecha": str(datetime.date.today()), "Servicio": serv.upper(), "Valor": monto}])
                conn.update(worksheet="Facturacion", data=pago)
                st.success("✅ Pago registrado.")
                st.cache_data.clear()
