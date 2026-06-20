import streamlit as st
import pandas as pd
import requests
import os

# Configuración API
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
st.set_page_config(page_title="Predicción de Colesterol", page_icon="🩺", layout="wide")
st.title("🩺 Predictor de Colesterol")
st.markdown("Ingrese los datos del paciente o cargue un archivo CSV para obtener estimaciones de colesterol.")

# 👉 Aquí sí va tu subheader
st.subheader("📂 Predicciones en lote")
archivo_csv = st.file_uploader("Suba un archivo CSV con datos de pacientes", type=["csv"])
