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

def extraer_prediccion(fila):
    if "prediction" in fila:
        return fila["prediction"]
    elif "predictionValues" in fila:
        return fila["predictionValues"][0]["value"]
    else:
        return None

def obtener_filas(resultado):
    if "data" in resultado:
        return resultado["data"]
    elif "predictions" in resultado:
        return resultado["predictions"]
    else:
        return []

# ==================================
# CONFIGURACIÓN STREAMLIT
# ==================================
st.set_page_config(page_title="Predicción de Colesterol", page_icon="🩺", layout="wide")

st.markdown("<h1 style='text-align: center; color: #2E86C1;'>🩺 Predictor de Colesterol</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Ingrese los datos del paciente o cargue un archivo CSV para obtener estimaciones de colesterol.</p>", unsafe_allow_html=True)

# ==================================
# ENTRADA MANUAL
# ==================================
st.markdown("### ✍️ Entrada Manual")
st.sidebar.header("Datos del Paciente")

genero = st.sidebar.selectbox("Género", ["Masculino", "Femenino"])
edad_anhos = st.sidebar.slider("Edad", 18, 100, 35)
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

# Codificación
genero = 1 if genero == "Masculino" else 0
fuma = 1 if fuma == "Sí" else 0
consume_alcohol = 1 if consume_al
