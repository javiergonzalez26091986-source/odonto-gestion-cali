import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Gestión Odontológica", page_icon="🦷")
st.title("🦷 Gestión - Odontología Familiar Especializada")

ID_CARPETA_DRIVE = "1hauuaIMZOztMBJSUANg0Ce7kquOAqYEu"

# --- CONEXIÓN A SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    df_pacientes = conn.read(worksheet="Pacientes", ttl=0)
    df_consultas = conn.read(worksheet="Consultas", ttl=0)
except Exception:
    df_pacientes = pd.DataFrame()
    df_consultas = pd.DataFrame()

# --- FUNCIÓN PARA MOSTRAR IMAGEN DE DRIVE ---
def mostrar_imagen_drive(id_foto):
    # Transforma el link compartido en un link directo que Streamlit puede leer
    url_directa = f"https://thumbnail.egnyte.com/dd/direct-link-for-drive/{id_foto}" 
    # Nota: Google ha restringido los links directos. 
    # Lo más seguro es mostrar el link para que se abra en pestaña nueva si falla la visualización.
    st.image(f"https://drive.google.com/thumbnail?id={id_foto}&sz=w1000", caption="Evidencia Clínica")

menu = st.sidebar.selectbox("Seleccione una opción", ["Registro de Pacientes", "Evolución de Pacientes", "Facturacion Interna"])

# (Módulo de Registro se mantiene igual)

if menu == "Evolución de Pacientes":
    st.header("📝 Historial y Evolución")
    
    if not df_pacientes.empty:
        paciente_sel = st.selectbox("Seleccione el Paciente", [""] + df_pacientes['Nombre'].unique().tolist())
        
        if paciente_sel != "":
            # Obtener cédula
            cedula_p = df_pacientes[df_pacientes['Nombre'] == paciente_sel]['Cédula'].values[0]
            
            # --- SECCIÓN 1: VER HISTORIAL ---
            st.subheader(f"Historial Clínico: {paciente_sel}")
            historial = df_consultas[df_consultas['Cédula'].astype(str) == str(cedula_p)]
            
            if not historial.empty:
                for index, row in historial.iterrows():
                    with st.expander(f"Consulta Fecha: {row['Fecha']}"):
                        st.write(f"**Motivo:** {row['Motivo']}")
                        st.write(f"**Diagnóstico:** {row['Diagnóstico']}")
                        st.write(f"**Tratamiento:** {row['Tratamiento']}")
                        
                        # Si el registro dice que hay foto, damos el botón para verla
                        st.info(f"Busca en Drive el archivo con Cédula: {cedula_p}")
                        st.markdown(f"🔗 [Abrir Carpeta de Fotos](https://drive.google.com/drive/folders/{ID_CARPETA_DRIVE})")
            else:
                st.info("No hay consultas registradas para este paciente.")

            # --- SECCIÓN 2: REGISTRAR NUEVA CONSULTA ---
            st.divider()
            st.subheader("Registrar Nueva Evolución")
            with st.form("nueva_ev"):
                f_ev = st.date_input("Fecha", datetime.date.today())
                motivo = st.text_area("Motivo de consulta")
                diag = st.text_area("Diagnóstico")
                trat = st.text_area("Tratamiento realizado")
                
                if st.form_submit_button("Guardar Evolución"):
                    nueva_fila = pd.DataFrame([{
                        "Cédula": str(cedula_p),
                        "Fecha": str(f_ev),
                        "Motivo": motivo.upper(),
                        "Diagnóstico": diag.upper(),
                        "Tratamiento": trat.upper(),
                        "Link_Foto": "VER EN DRIVE"
                    }])
                    conn.update(worksheet="Consultas", data=nueva_fila)
                    st.success("Consulta guardada.")
                    st.cache_data.clear()

# (Módulo de Facturación se mantiene igual)
