import streamlit as st
import pandas as pd
import requests
import os


# ==================================
# CONFIGURACIÓN API DATAROBOT
# ==================================

API_KEY = "TU_TOKEN_GENERADO"
DEPLOYMENT_ID = "6a35a3e185191304741588d4"
HOST = "https://app.datarobot.com"

headers = {"Authorization": f"Token {API_KEY}", "Content-Type": "application/json"} url = f"{HOST}/api/v2/deployments/{DEPLOYMENT_ID}/predictions"

resp = requests.post(url, headers=headers, json=data)

st.write(resp.text)

data = {"data":[{"edad_anhos":30,"peso_kg":70,"estatura_cm":170}]}
resp = requests.post(url, headers=headers, json=data)

print(resp.status_code)
print(resp.text)

def hacer_prediccion(datos):
    url = f"{HOST}/api/v2/deployments/{DEPLOYMENT_ID}/predictions"
    response = requests.post(url, headers=headers, json={"data": datos})
    if response.status_code != 200:
        return {"error": response.text}
    return response.json()

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
consume_alcohol = 1 if consume_alcohol == "Sí" else 0
enfermedad_cardiaca = 1 if enfermedad_cardiaca == "Sí" else 0
actividad_map = {"Baja": 0, "Media": 1, "Alta": 2}
actividad_fisica = actividad_map[actividad_fisica]

datos_manual = pd.DataFrame([{
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
    "edad_anhos": edad_anhos,
    "indice_masa_corporal": indice_masa_corporal
}])

# Mostrar datos y predicción manual
col1, col2 = st.columns([2, 1])
with col1:
    st.subheader("Variables ingresadas (manual)")
    st.dataframe(datos_manual, use_container_width=True)

with col2:
    if st.button("🔍 Predecir Colesterol (manual)", key="btn_manual"):
        resultado = hacer_prediccion(datos_manual.to_dict(orient="records"))
        if "error" in resultado:
            st.error(f"Error en la predicción: {resultado['error']}")
        else:
            prediccion = resultado.get("data", [{}])[0].get("prediction", None)
            if prediccion is not None:
                st.metric(label="Colesterol Estimado", value=f"{prediccion:.2f} mg/dL")
                if prediccion < 200:
                    st.success("✅ Nivel deseable")
                elif prediccion < 240:
                    st.warning("⚠️ Nivel límite alto")
                else:
                    st.error("❌ Nivel alto")
            else:
                st.error("No se encontró la clave 'prediction' en la respuesta.")

# ==================================
# PREDICCIONES EN LOTE DESDE CSV
# ==================================
st.markdown("### 📂 Predicciones en Lote")
archivo_csv = st.file_uploader("Suba un archivo CSV con datos de pacientes", type=["csv"])

if archivo_csv is not None:
    datos_csv = pd.read_csv(archivo_csv)
    st.write("Datos cargados:")
    st.dataframe(datos_csv.head(), use_container_width=True)

    if st.button("🔍 Predecir desde CSV", key="btn_csv"):
        resultado = hacer_prediccion(datos_csv.to_dict(orient="records"))
        if "error" in resultado:
            st.error(f"Error en la predicción: {resultado['error']}")
        else:
            predicciones = []
            for fila in resultado.get("data", []):
                if "prediction" in fila:
                    predicciones.append(fila["prediction"])
                elif "predictions" in fila:
                    predicciones.append(fila["predictions"][0].get("value", None))
                else:
                    predicciones.append(None)

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

