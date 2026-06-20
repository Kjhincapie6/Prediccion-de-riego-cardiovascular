# ==================================
# CONFIGURACIÓN STREAMLIT
# ==================================
st.set_page_config(page_title="Predicción de Colesterol", page_icon="🩺", layout="wide")

# Encabezado principal
st.markdown("<h1 style='text-align: center; color: #2E86C1;'>🩺 Predictor de Colesterol</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Ingrese los datos del paciente o cargue un archivo CSV para obtener estimaciones de colesterol.</p>", unsafe_allow_html=True)

# ==================================
# SECCIÓN DE ENTRADA MANUAL
# ==================================
st.markdown("### ✍️ Entrada Manual")
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Datos del Paciente")
    # Aquí van tus sliders y selectboxes (como ya los definimos antes)

with col2:
    st.subheader("Predicción")
    if st.button("🔍 Predecir Colesterol (manual)"):
        resultado = hacer_prediccion(datos_manual.to_dict(orient="records"))
        prediccion = resultado["data"][0]["prediction"]

        st.metric(label="Colesterol Estimado", value=f"{prediccion:.2f} mg/dL")

        if prediccion < 200:
            st.success("✅ Nivel deseable")
        elif prediccion < 240:
            st.warning("⚠️ Nivel límite alto")
        else:
            st.error("❌ Nivel alto")

# ==================================
# SECCIÓN DE CSV
# ==================================
st.markdown("### 📂 Predicciones en Lote")
archivo_csv = st.file_uploader("Suba un archivo CSV con datos de pacientes", type=["csv"])

if archivo_csv is not None:
    datos_csv = pd.read_csv(archivo_csv)
    st.write("Datos cargados:")
    st.dataframe(datos_csv.head(), use_container_width=True)

    if st.button("🔍 Predecir desde CSV"):
        resultado = hacer_prediccion(datos_csv.to_dict(orient="records"))
        predicciones = [fila["prediction"] for fila in resultado["data"]]
        datos_csv["colesterol_estimado"] = predicciones

        st.success("✅ Predicciones generadas correctamente")
        st.dataframe(datos_csv, use_container_width=True)

        st.download_button(
            label="⬇️ Descargar resultados",
            data=datos_csv.to_csv(index=False).encode("utf-8"),
            file_name="resultados_colesterol.csv",
            mime="text/csv"
        )

# ==================================
# PIE DE PÁGINA
# ==================================
st.markdown("---")
st.caption("✨ Modelo Predictivo de Colesterol conectado a DataRobot y desplegado con Streamlit.")
