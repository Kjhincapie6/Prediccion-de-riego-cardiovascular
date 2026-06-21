import streamlit as st
import pandas as pd
import requests
import os

# ==================================
# CONFIGURACIÓN DATAROBOT
# ==================================
API_KEY = os.getenv("DATAROBOT_API_KEY")
DEPLOYMENT_ID = os.getenv("DATAROBOT_DEPLOYMENT_ID")
HOST = os.getenv("DATAROBOT_HOST")

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# ==================================
# FUNCIÓN DE PREDICCIÓN
# ==================================
def hacer_prediccion(df):

    url = f"{HOST}/api/v2/deployments/{DEPLOYMENT_ID}/predictions"

    df = df.copy()

    # 🔥 MAPEO CORRECTO DATAROBOT
    df = df.rename(columns={
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

    # DEBUG (puedes quitarlo en producción)
    st.write("🔍 STATUS:", response.status_code)
    st.write("🔍 RESPONSE:", response.text)

    if response.status_code != 200:
        return {"error": response.text}

    return response.json()


# ==================================
# UI STREAMLIT (MISMO DISEÑO ORIGINAL)
# ==================================
st.set_page_config(
    page_title="Predicción de Riesgo Cardiovascular",
    page_icon="🩺",
    layout="wide"
)

st.markdown(
    "<h1 style='text-align: center; color: #2E86C1;'>🩺 Predictor de Riesgo Cardiovascular</h1>",
    unsafe_allow_html=True
)

st.markdown(
    "<p style='text-align: center;'>Ingrese los datos del paciente o cargue un archivo CSV para estimar el riesgo cardiovascular.</p>",
    unsafe_allow_html=True
)

# ==================================
# ENTRADA MANUAL (SIDEBAR ORIGINAL)
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

# ==================================
# DATAFRAME MANUAL
# ==================================
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
# RESULTADO MANUAL (DISEÑO ORIGINAL)
# ==================================
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Variables ingresadas (manual)")
    st.dataframe(datos_manual, use_container_width=True)

with col2:
    if st.button("🔍 Predecir Riesgo", key="btn_manual"):

        resultado = hacer_prediccion(datos_manual)

        if "error" in resultado:
            st.error(resultado["error"])
        else:

            fila = resultado["data"][0]

            pred = fila["prediction"]
            probs = fila.get("predictionValues", [])

            prob_riesgo = None
            for p in probs:
                if str(p.get("label")) in ["1", "1.0", 1]:
                    prob_riesgo = p.get("value")

            st.subheader("Resultado del modelo")

            st.metric("Clase de riesgo", str(pred))

            if prob_riesgo is not None:
                st.progress(float(prob_riesgo))
                st.write(f"📊 Probabilidad de riesgo: {prob_riesgo:.2%}")

            if pred == 1:
                st.error("🔴 Alto riesgo cardiovascular")
                st.markdown("⚠️ Interpretación clínica: paciente con riesgo elevado según el modelo.")
            else:
                st.success("🟢 Bajo riesgo cardiovascular")
                st.markdown("✅ Interpretación clínica: paciente con riesgo controlado según el modelo.")

# ==================================
# PREDICCIÓN CSV (DISEÑO ORIGINAL)
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
            st.error(resultado["error"])
        else:

            predicciones = []
            probabilidades = []

            for fila in resultado["data"]:

                pred = fila["prediction"]
                probs = fila.get("predictionValues", [])

                prob_riesgo = None
                for p in probs:
                    if str(p.get("label")) in ["1", "1.0", 1]:
                        prob_riesgo = p.get("value")

                predicciones.append(pred)
                probabilidades.append(prob_riesgo)

            datos_csv["riesgo_predicho"] = predicciones
            datos_csv["probabilidad_riesgo"] = probabilidades

            st.success("✅ Predicciones generadas correctamente")
            st.dataframe(datos_csv, use_container_width=True)

            st.download_button(
                label="⬇️ Descargar resultados",
                data=datos_csv.to_csv(index=False).encode("utf-8"),
                file_name="resultados_riesgo.csv",
                mime="text/csv"
            )

# ==================================
# FOOTER
# ==================================
st.markdown("---")
st.caption("✨ Modelo predictivo de riesgo cardiovascular conectado a DataRobot + Streamlit")
