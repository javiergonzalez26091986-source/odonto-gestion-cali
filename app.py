# --- MÓDULO 2: EVOLUCIÓN DE PACIENTES ---
elif menu == "Evolución de Pacientes":
    st.header("📝 Evolución y Consultas")
    if not df_pacientes.empty:
        nombres_validos = df_pacientes['Nombre'].dropna().unique().tolist()
        paciente_sel = st.selectbox("Seleccione el Paciente", [""] + nombres_validos)
        
        if paciente_sel != "":
            # Obtener datos del paciente seleccionado
            datos_p = df_pacientes[df_pacientes['Nombre'] == paciente_sel].iloc[0]
            cedula_p = str(datos_p['Cédula']).split('.')[0] # Limpiamos el .0 si existe
            
            st.subheader(f"Paciente: {paciente_sel} (CC: {cedula_p})")

            # --- NUEVA SECCIÓN: VISUALIZACIÓN DE HISTORIAL Y FOTOS ---
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown("### 📜 Historial")
                try:
                    df_consultas = conn.read(worksheet="Consultas", ttl=0)
                    historial = df_consultas[df_consultas['Cédula'].astype(str).str.contains(cedula_p)]
                    if not historial.empty:
                        for i, fila in historial.iterrows():
                            with st.expander(f"Consulta: {fila['Fecha']}"):
                                st.write(f"**Motivo:** {fila['Motivo']}")
                                st.write(f"**Tratamiento:** {fila['Tratamiento']}")
                    else:
                        st.info("No hay consultas previas.")
                except:
                    st.info("Aún no hay registros en la hoja de Consultas.")

            with col2:
                st.markdown("### 📸 Evidencia en Drive")
                # Botón directo a la búsqueda en Drive por Cédula
                url_busqueda = f"https://drive.google.com/drive/search?q={cedula_p}"
                st.link_button("📂 Ver fotos de este paciente", url_busqueda)
                
                # Mensaje de ayuda
                st.caption(f"Al hacer clic, se abrirá Drive con los archivos que tengan la cédula {cedula_p}")

            st.divider()
            
            # --- FORMULARIO DE NUEVA CONSULTA (El que ya tenías) ---
            st.subheader("Registrar Nueva Evolución")
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
        st.warning("No hay pacientes registrados.")
