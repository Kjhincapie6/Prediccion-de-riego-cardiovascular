# ==================================
# PREDICCIONES EN LOTE DESDE CSV
# ==================================
st.subheader("📂 Predicciones en lote")
archivo_csv = st.file_uploader("Suba un archivo CSV con datos de pacientes", type=["csv"])

if archivo_csv is not None:
    # Leer archivo
    datos_csv = pd.read_csv(archivo_csv)
    st.write("Datos cargados:")
    st.dataframe(datos_csv.head(), use_container_width=True)

    # Botón para ejecutar predicción
    if st.button("🔍 Predecir desde CSV"):
        # Enviar datos a DataRobot
        resultado = hacer_prediccion(datos_csv.to_dict(orient="records"))
        predicciones = [fila["prediction"] for fila in resultado["data"]]

        # Agregar columna de predicciones
        datos_csv["colesterol_estimado"] = predicciones

        # Mostrar resultados
        st.write("Resultados con predicciones:")
        st.dataframe(datos_csv, use_container_width=True)

        # Descargar resultados
        st.download_button(
            label="⬇️ Descargar resultados",
            data=datos_csv.to_csv(index=False).encode("utf-8"),
            file_name="resultados_colesterol.csv",
            mime="text/csv"
        )
