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
# FUNCIÓN DE PREDICCIÓN (CORREGIDA)
# ==================================
def hacer_prediccion(df):
    url = f"{HOST}/api/v2/deployments/{DEPLOYMENT_ID}/predictions"
    df = df.copy()

    # =========================
    # FIX CRÍTICO: NORMALIZAR EDAD
    # =========================
    if "edad_dias" not in df.columns:
        if "edad_anhios" in df.columns:
            df["edad_dias"] = df["edad_anhios"] * 365
        elif "edad_anios" in df.columns:
            df["edad_anios"] = df["edad_anios"] * 365
        else:
            return {"error": "El archivo CSV no contiene edad válida (edad_anhios o edad_anios)"}

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

# ========================================================
# FIX DE UX/UI: MAPEO DE COLESTEROL (Muestra texto, envía número)
# ========================================================
colesterol_map = {
    "Normal": 1,
    "Por encima de lo normal": 2,
    "Muy superior a lo normal": 3
}
colesterol_visual = st.sidebar.selectbox("Nivel de Colesterol", list(colesterol_map.keys()))
colesterol_modelo = colesterol_map[colesterol_visual]

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
    "edad_dias": edad_anios * 365,
    "genero": genero,
    "estatura_cm": estatura_cm,
    "peso_kg": peso_kg,
    "presion_sistolica": presion_sistolica,
    "presion_diastolica": presion_diastolica,
    "colesterol": colesterol_modelo,  # Envía el valor numérico (1, 2 o 3) requerido por DataRobot
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
    datos_ui = datos_manual.copy()
    datos_ui["edad_anios"] = edad_anios
    datos_ui = datos_ui.drop(columns=["edad_dias"])
    st.dataframe(datos_ui, use_container_width=True, hide_index=True)

with col2:
    debug = st.checkbox("🔧 Mostrar debug técnico")

    if st.button("🔍 Predecir Riesgo"):
        resultado = hacer_prediccion(datos_manual)

        if "error" in resultado:
            st.error(resultado["error"])
        else:
            if debug:
                st.json(resultado)

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
            else:
                st.success("🟢 Bajo riesgo cardiovascular")
# ==================================
# RECOMENDACIONES PERSONALIZADAS
# ==================================

sif pred == 1:
    st.error("🔴 Alto riesgo cardiovascular")

    st.markdown("---")
    st.subheader("❤️ Recomendaciones Personalizadas")

    recomendaciones = []

    if presion_sistolica >= 140 or presion_diastolica >= 90:
        recomendaciones.append(
            "🩺 **Controle su presión arterial.** Sus valores se encuentran elevados y es recomendable consultar a un profesional de la salud."
        )

    if colesterol_modelo >= 2:
        recomendaciones.append(
            "🥗 **Mejore su alimentación.** Reduzca grasas saturadas y aumente el consumo de frutas, verduras y fibra."
        )

    if glucosa >= 126:
        recomendaciones.append(
            "🍬 **Controle sus niveles de glucosa.** Es recomendable realizar una valoración médica."
        )

    if fuma == 1:
        recomendaciones.append(
            "🚭 **Deje de fumar.** El tabaquismo incrementa significativamente el riesgo cardiovascular."
        )

    if consume_alcohol == 1:
        recomendaciones.append(
            "🍺 **Reduzca el consumo de alcohol.**"
        )

    if actividad_fisica == 0:
        recomendaciones.append(
            "🏃 **Aumente su actividad física.** Se recomienda al menos 150 minutos de ejercicio moderado por semana."
        )

    imc = peso_kg / ((estatura_cm / 100) ** 2)

    if imc >= 25:
        recomendaciones.append(
            f"⚖️ **Su IMC es {imc:.1f}.** Se recomienda trabajar en alcanzar un peso saludable."
        )

    for r in recomendaciones:
        st.write(r)

    st.info(
        "⚠️ Estas recomendaciones son orientativas y no reemplazan la valoración de un profesional de la salud."
    )

else:
    st.success("🟢 Bajo riesgo cardiovascular")
    st.balloons()
    st.info(
        "🎉 El modelo estima un riesgo cardiovascular bajo. Continúe manteniendo hábitos saludables y realice controles médicos periódicos."
    )

# ==================================
# PREDICCIÓN EN LOTE
# ==================================
st.markdown("### 📂 Predicciones en Lote")
archivo_csv = st.file_uploader("Suba un archivo CSV con datos de pacientes", type=["csv"])

if archivo_csv is not None:
    datos_csv = pd.read_csv(archivo_csv)
    st.dataframe(datos_csv.head(), use_container_width=True, hide_index=True)

    if st.button("🔍 Predecir desde CSV"):
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


# ==================================
# AUTOR (CONSOLIDADO)
# ==================================
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
<a href="https://wa.me/573015704518?text=Hola%20Kely,%20he%20visto%20tu%20proyecto%20de%20Machine%20Learning%20y%20quisiera%20más%20información."
target="_blank"
style="background:#25D366;color:white;padding:10px 18px;border-radius:8px;text-decoration:none;font-weight:600;margin-right:10px;">
💬 WhatsApp Business
</a>

🚀 <b>Proyecto:</b> Modelo Predictivo de Riesgo Cardiovascular basado en Machine Learning,
desplegado en Streamlit Cloud e integrado con DataRobot.

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
