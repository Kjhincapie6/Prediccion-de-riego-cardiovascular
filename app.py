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

def hacer_prediccion(datos):
    url = f"{HOST}/api/v2/deployments/{DEPLOYMENT_ID}/predictions"
    response = requests.post(url, headers=headers, json={"data": datos})
    return response.json()

# ==================================
# CONFIGURACIÓN STREAMLIT
# ==================================
st.set_page_config(
    page_title="Predicción de Colesterol",
    page_icon="🩺",
    layout="wide"
)

st.title("🩺 Predictor de Colesterol")
st.markdown("Ingrese los datos del paciente y obtenga una estimación del colesterol.")

# ==================================
# SIDEBAR
# ==================================
st.sidebar.header("Datos del Paciente")

genero = st.sidebar.selectbox("Género", ["Masculino", "Femenino"])
edad_anhios = st.sidebar.slider("Edad", 18, 100, 35)
estatura_cm = st.sidebar.slider("Estatura (cm)", 120, 220, 170)
peso_kg = st.sidebar.slider("Peso (kg)", 30, 200, 70)
presion_sistolica = st.sidebar.slider("Presión Sistólica", 80, 220, 120)
presion_diastolica = st.sidebar.slider("Presión Diastólica", 50, 150, 80)
glucosa = st.sidebar.slider("Glucosa", 50, 300, 100)
fuma = st.sidebar.selectbox("¿Fuma?", ["No", "Sí"])
consume_alcohol = st.sidebar.selectbox("¿Consume Alcohol?", ["No", "Sí"])
actividad_fisica = st.sidebar.selectbox("Actividad Física", ["Baja", "Media", "Alta"])
enfermedad_cardiaca = st.sidebar.selectbox("¿Enfermedad Cardíaca?", ["No", "Sí"])
indice_masa_corporal = st.sidebar.number_input("IMC", min_value=10.0, max_value=60.0, value=24.5)

# ==================================
# CODIFICACIÓN
# ==================================
genero = 1 if genero == "Masculino" else 0
fuma = 1 if fuma == "Sí" else 0
consume_alcohol = 1 if consume_alcohol == "Sí" else 0
enfermedad_cardiaca = 1 if enfermedad_cardiaca == "Sí" else 0
actividad_map = {"Baja": 0, "Media": 1, "Alta": 2}
actividad_fisica = actividad_map[actividad_fisica]

# ==================================
# DATAFRAME DE ENTRADA
# ==================================
datos = pd.DataFrame([{
    "genero": genero,
    "estatura_cm": estatura_cm,
    "peso_kg": peso_kg,
    "presion_sistolica": presion_sistolica,
    "presion_diastolica": presion_diastolica,
    "glucosa": glucosa,
    "fuma": fuma,
    "consume_alcohol": consume_alcohol,
    "actividad_fisica": actividad_fisica,
    "enfermedad_cardiaca": enfermedad_cardiaca,
    "edad_anhios": edad_anhios,
    "indice_masa_corporal": indice_masa_corporal
}])

# ==================================
# MOSTRAR DATOS Y PREDICCIÓN
# ==================================
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Variables ingresadas")
    st.dataframe(datos, use_container_width=True)

with col2:
    if st.button("🔍 Predecir Colesterol"):
        resultado = hacer_prediccion(datos.to_dict(orient="records"))
        prediccion = resultado["data"][0]["prediction"]

        st.metric(label="Colesterol Estimado", value=f"{prediccion:.2f} mg/dL")

        if prediccion < 200:
            st.success("Nivel deseable")
        elif prediccion < 240:
            st.warning("Nivel límite alto")
        else:
            st.error("Nivel alto")

# ==================================
# PIE DE PÁGINA
# ==================================
st.markdown("---")
st.caption("Modelo Predictivo de Colesterol conectado a DataRobot y desplegado con Streamlit.")
