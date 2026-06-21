import streamlit as st
import pandas as pd
import requests
import os

# ==================================
# CONFIGURACIÓN API DATAROBOT
# ==================================
API_KEY = os.getenv("DATAROBOT_API_KEY")
DEPLOYMENT_ID = os.getenv("DATAROBOT_DEPLOYMENT_ID")
HOST = os.getenv("DATAROBOT_HOST")

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def hacer_prediccion(df):
    url = f"{HOST}/api/v2/deployments/{DEPLOYMENT_ID}/predictions"

    df = df.rename(columns={
        "id_paciente": "id",
        "edad_dias": "age",
        "genero": "gender",
        "estatura_cm": "height",
        "peso_kg": "weight",
        "presion_sistolica": "ap_hi",
        "presion_diastolica": "ap_lo",
        "colesterol": "cholesterol",
        "glucosa": "gluc",
        "fuma": "smoke",
        "consume_alcohol": "alco",
        "actividad_fisica": "active",
        "enfermedad_cardiovascular": "cardio"
    })

    datos = df.to_dict(orient="records")

    response = requests.post(url, headers=headers, json=datos)

    if response.status_code != 200:
        return {"error": response.text}

    return response.json()


# ==================================
# CONFIGURACIÓN STREAMLIT
# ==================================
st.set_page_config(
    page_title="Predicción de Colesterol",
    page_icon="🩺",
    layout="wide"
)

st.markdown(
    "<h1 style='text-align: center; color: #2E86C1;'>🩺 Predictor de Colesterol</h1>",
    unsafe_allow_html=True
)

st.markdown(
    "<p style='text-align: center;'>Ingrese los datos del paciente o cargue un archivo CSV para obtener estimaciones de colesterol.</p>",
    unsafe_allow_html=True
)

# ==================================
# ENTRADA MANUAL
# ==================================
st.markdown("### ✍️ Entrada Manual")
st.sidebar.header("Datos del Paciente")

genero = st.sidebar.selectbox("Género", ["Masculino", "Femenino"])
edad_dias = st.sidebar.slider("Edad (días)", 6570, 36500, 15000)
estatura_cm = st.sidebar.slider("Estatura (cm)", 120, 220, 170)
peso_kg = st.sidebar.slider("Peso (kg)", 30, 200, 70)
presion_sistolica = st.sidebar.slider("Presión Sistólica", 80, 220, 120)
presion_diastolica = st.sidebar.slider("Presión Diastólica", 50, 150, 80)
glucosa = st.sidebar.slider("Glucosa", 50, 300, 100)
fuma = st.sidebar.selectbox("¿Fuma?", ["No", "Sí"])
consume_alcohol = st.sidebar.selectbox("¿Consume Alcohol?", ["No", "Sí"])
actividad_fisica = st.sidebar.selectbox("Actividad Física", ["Baja", "Media", "Alta"])
enfermedad_cardiovascular = st.sidebar.selectbox("¿Enfermedad Cardiovascular?", ["No", "Sí"])
colesterol = st.sidebar.selectbox("Colesterol (input modelo)", [1, 2, 3])

# ==================================
# CODIFICACIÓN
# ==================================
genero = 1 if genero == "Masculino" else 0
fuma = 1 if fuma == "Sí" else 0
consume_alcohol = 1 if consume_alcohol == "Sí" else 0
enfermedad_cardiovascular = 1 if enfermedad_cardiovascular == "Sí" else 0

actividad_map = {"Baja": 0, "Media": 1, "Alta": 2}
actividad_fisica = actividad_map[actividad_fisica]

datos_manual = pd.DataFrame([{
    "id_paciente": 1,
    "edad_dias": edad_dias,
    "genero": genero,
    "estatura_cm": estatura_cm,
    "peso_kg": peso_kg,
    "presion_sistolica": presion_sistolica,
    "presion_diastolica": presion_diastolica,
    "colesterol": colesterol,
    "glucosa": glucosa,
    "fuma": fuma,
    "consume_alcohol": consume_alcohol,
    "actividad_fisica": actividad_fisica,
    "enfermedad_cardiovascular": enfermedad_cardiovascular
}])

# ==================================
# RESULTADO MANUAL
# ==================================
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Variables ingresadas (manual)")
    st.dataframe(datos_manual, use_container_width=True)

with col2:
    if st.button("🔍 Predecir Colesterol (manual)", key="btn_manual"):
        resultado = hacer_prediccion(datos_manual)

        if "error" in resultado:
            st.error(f"Error en la predicción: {resultado['error']}")
        else:
            fila = resultado.get("data", [{}])[0]

            pred = fila.get("prediction")

            # Intentar convertir a número (regresión)
            try:
                pred_num = float(pred)
            except:
                pred_num = None

            st.subheader("Resultado")

            if pred_num is not None:
                st.metric("Colesterol Estimado", f"{pred_num:.2f} mg/dL")

                if pred_num < 200:
                    st.success("✅ Nivel deseable")
                elif pred_num < 240:
                    st.warning("⚠️ Nivel límite alto")
                else:
                    st.error("❌ Nivel alto")
            else:
                # Clasificación
                pred_alt = fila.get("predictionValues", [{}])[0].get("value")

                st.metric("Resultado", str(pred_alt))

                if str(pred_alt) in ["1", "Yes", "True", "Alto"]:
                    st.error("❌ Riesgo alto")
                else:
                    st.success("✅ Nivel controlado")

# ==================================
# PREDICCIONES EN LOTE
# ==================================
st.markdown("### 📂 Predicciones en Lote")

archivo_csv = st.file_uploader("Suba un archivo CSV con datos de pacientes", type=["csv"])

if archivo_csv is not None:
    datos_csv = pd.read_csv(archivo_csv)

    st.write("Datos cargados:")
    st.dataframe(datos_csv.head(), use_container_width=True)

    if st.button("🔍 Predecir desde CSV", key="btn_csv"):
        resultado = hacer_prediccion(datos_csv)

        if "error" in resultado:
            st.error(f"Error en la predicción: {resultado['error']}")
        else:
            predicciones = []

            for fila in resultado.get("data", []):
                pred = fila.get("prediction")

                try:
                    pred = float(pred)
                except:
                    pred = fila.get("predictionValues", [{}])[0].get("value")

                predicciones.append(pred)

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
st.caption("✨ Modelo Predictivo conectado a DataRobot y desplegado con Streamlit.")
