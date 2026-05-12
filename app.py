# ---------------------------------------------------------
# MÓDULO 3: AGENDA DE CITAS (Actualizado)
# ---------------------------------------------------------
elif menu == "Agenda de Citas":
    st.header("📅 Agenda de Citas")
    
    # 1. Cargamos pacientes para el selector
    try:
        df_pacientes = conn.read(worksheet="Pacientes", ttl=0)
        lista_pacientes = df_pacientes['Nombre'].tolist() if not df_pacientes.empty else []
    except:
        lista_pacientes = []

    tab1, tab2 = st.tabs(["➕ Agendar Nueva", "📋 Ver Agenda"])

    with tab1:
        with st.form("form_cita"):
            col_c1, col_c2 = st.columns(2)
            with col_c1:
                # El usuario elige de la lista de pacientes ya registrados
                paciente_sel = st.selectbox("Seleccionar Paciente", lista_pacientes)
                fecha_cita = st.date_input("Fecha de la Cita", min_value=datetime.date.today())
            with col_c2:
                hora_cita = st.time_input("Hora de la Cita", value=datetime.time(8, 0))
                procedimiento = st.selectbox("Procedimiento", ["Valoración", "Limpieza", "Extracción", "Resina", "Ortodoncia", "Otro"])
            
            notas_cita = st.text_area("Notas adicionales")
            
            if st.form_submit_button("Agendar Cita"):
                if paciente_sel:
                    # Buscamos la cédula del paciente seleccionado
                    cedula_sel = df_pacientes[df_pacientes['Nombre'] == paciente_sel]['Cédula'].values[0]
                    
                    nueva_cita = pd.DataFrame([{
                        "Paciente": paciente_sel,
                        "Cédula": str(cedula_sel),
                        "Fecha": str(fecha_cita),
                        "Hora": str(hora_cita),
                        "Procedimiento": procedimiento,
                        "Observaciones": notas_cita,
                        "Estado": "PENDIENTE"
                    }])
                    
                    conn.update(worksheet="Citas", data=nueva_cita)
                    st.success(f"✅ Cita agendada para {paciente_sel} el {fecha_cita}")
                else:
                    st.error("Primero debe registrar al paciente en el módulo de Registro.")

    with tab2:
        st.subheader("Citas Programadas")
        try:
            df_citas = conn.read(worksheet="Citas", ttl=0)
            if not df_citas.empty:
                # Mostramos la tabla de citas
                st.dataframe(df_citas, use_container_width=True)
            else:
                st.info("No hay citas programadas.")
        except:
            st.warning("Cree la pestaña 'Citas' en su Google Sheets para ver la agenda.")

Sube estos cambios y ya podrás empezar a llenar tu agenda digital. ¿Qué te parece cómo quedó la presentación estratégica?
