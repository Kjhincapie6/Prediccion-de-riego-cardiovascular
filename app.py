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

    # Debug seguro
    with st.expander("🔧 Información técnica"):
        st.code(f"STATUS: {response.status_code}")
        try:
            st.json(response.json())
        except Exception:
            st.text(response.text)

    if response.status_code != 200:
        return {"error": response.text}

    return response.json()


# ==================================
# CONFIGURACIÓN STREAMLIT
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
# ENTRADA MANUAL
# ==================================
st.markdown("### ✍️ Entrada Manual")
st.sidebar.header("Datos del Paciente")

genero = st.sidebar.selectbox("Género", ["Masculino", "Femenino"])

# 🔥 CAMBIO PRINCIPAL: edad en años
edad_anios = st.sidebar.slider("Edad (años)", 18, 100, 40)

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

    # 🔥 conversión obligatoria para DataRobot
    "edad_dias": edad_anios * 365,

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
# UI RESULTADO
# ==================================
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Variables ingresadas (manual)")

    # Mostrar edad en años en UI (más limpio)
    datos_ui = datos_manual.copy()
    datos_ui["edad_anios"] = edad_anios
    datos_ui = datos_ui.drop(columns=["edad_dias"])

    st.dataframe(datos_ui, use_container_width=True, hide_index=True)

with col2:
    if st.button("🔍 Predecir Riesgo"):

        resultado = hacer_prediccion(datos_manual)

        if "error" in resultado:
            st.error(resultado["error"])
        else:

            fila = resultado["data"][0]

            pred = fila["prediction"]
            probs = fila.get("predictionValues", [])

            prob_riesgo = None
            for p in probs:
                if p.get("label") in [1, "1", 1.0, "1.0"]:
                    prob_riesgo = p.get("value")

            if prob_riesgo is None and len(probs) > 0:
                prob_riesgo = max(probs, key=lambda x: x.get("value", 0)).get("value")

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
# PREDICCIÓN EN LOTE
# ==================================
st.markdown("### 📂 Predicciones en Lote")

archivo_csv = st.file_uploader("Suba un archivo CSV con datos de pacientes", type=["csv"])

if archivo_csv is not None:

    datos_csv = pd.read_csv(archivo_csv)

    st.dataframe(datos_csv.head(), use_container_width=True, hide_index=True)

    if st.button("🔍 Predecir desde CSV"):

        # asegurar id si no existe
        if "id_paciente" not in datos_csv.columns:
            datos_csv["id_paciente"] = range(1, len(datos_csv) + 1)

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
                    if p.get("label") in [1, "1", 1.0, "1.0"]:
                        prob_riesgo = p.get("value")

                if prob_riesgo is None and len(probs) > 0:
                    prob_riesgo = max(probs, key=lambda x: x.get("value", 0)).get("value")

                predicciones.append(pred)
                probabilidades.append(prob_riesgo)

            datos_csv["riesgo_predicho"] = predicciones
            datos_csv["probabilidad_riesgo"] = probabilidades

            st.success("✅ Predicciones generadas correctamente")

            st.dataframe(datos_csv, use_container_width=True, hide_index=True)

            st.download_button(
                label="⬇️ Descargar resultados",
                data=datos_csv.to_csv(index=False).encode("utf-8"),
                file_name="resultados_riesgo.csv",
                mime="text/csv"
            )
st.markdown("""
<style>
.autor-card {
    background-color: #ffffff;
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #E5E7EB;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.08);
    margin-top: 30px;
}

.autor-nombre {
    font-size: 22px;
    font-weight: 700;
    color: #0F172A;
}

.autor-profesion {
    font-size: 14px;
    color: #475569;
    margin-bottom: 15px;
}

.autor-info {
    font-size: 14px;
    color: #334155;
    line-height: 1.8;
}

.linkedin-btn {
    display: inline-block;
    padding: 8px 16px;
    background-color: #0077B5;
    color: white !important;
    text-decoration: none;
    border-radius: 8px;
    margin-top: 10px;
    font-weight: 600;
}
</style>

<div class="autor-card">

<div class="autor-nombre">
Desarrollado por Kely Jhojana Hincapié Zapata
</div>

<div class="autor-profesion">
Especialista en Analítica de Datos | Profesional en Administración Financiera |
Tecnóloga en Gestión de Redes de Datos
</div>

<div class="autor-info">

<div style="margin-top:10px;">

<a href="https://wa.me/573015704518?text=Hola%20Kely,%20he%20visto%20tu%20proyecto%20de%20Machine%20Learning%20y%20quisiera%20más%20información."
target="_blank"
style="
background:#25D366;
color:white;
padding:10px 18px;
border-radius:8px;
text-decoration:none;
font-weight:600;
margin-right:10px;">
💬 WhatsApp Business
</a>

<a href="https://www.linkedin.com/in/kely-jhojana-hincapi%C3%A9-zapata-502587130/"
target="_blank"
style="
background:#0077B5;
color:white;
padding:10px 18px;
border-radius:8px;
text-decoration:none;
font-weight:600;">
LinkedIn
</a>

</div>

🚀 <b>Proyecto:</b> Modelo predictivo de riesgo cardiovascular desarrollado 
mediante técnicas de Machine Learning supervisado para clasificación binaria, entrenado sobre variables
clínicas y hábitos de vida, desplegado en DataRobot y consumido a 
través de una aplicación interactiva en Streamlit Cloud.

<br>

<a class="linkedin-btn"
href="https://www.linkedin.com/in/kely-jhojana-hincapi%C3%A9-zapata-502587130/"
target="_blank">
LinkedIn Profesional
</a>

</div>

</div>
""", unsafe_allow_html=True)
# ==================================
# FOOTER
# ==================================
st.markdown("---")
st.caption("""
✨ Modelo predictivo de riesgo cardiovascular basado en técnicas de Machine Learning para clasificación binaria,
entrenado con variables clínicas y hábitos de vida.

La solución fue desplegada mediante DataRobot y consumida a través de una aplicación interactiva
desarrollada en Streamlit Cloud.
""")
