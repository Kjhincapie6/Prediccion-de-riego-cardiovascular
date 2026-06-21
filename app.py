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
# HISTORIAL EN SESIÓN
# ==================================
if "historial" not in st.session_state:
    st.session_state.historial = []

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

    with st.expander("🔧 Debug técnico"):
        st.code(f"STATUS: {response.status_code}")
        try:
            st.json(response.json())
        except Exception:
            st.text(response.text)

    if response.status_code != 200:
        return {"error": response.text}

    return response.json()


# ==================================
# UI GENERAL
# ==================================
st.set_page_config(
    page_title="Riesgo Cardiovascular PRO",
    page_icon="🩺",
    layout="wide"
)

st.markdown(
    "<h1 style='text-align:center;color:#2E86C1;'>🩺 Predictor de Riesgo Cardiovascular PRO</h1>",
    unsafe_allow_html=True
)

st.markdown(
    "<p style='text-align:center;'>Dashboard analítico conectado a DataRobot</p>",
    unsafe_allow_html=True
)

tabs = st.tabs(["🧍 Manual", "📂 CSV", "📊 Métricas"])

# ==================================
# TAB 1 - MANUAL
# ==================================
with tabs[0]:

    st.sidebar.header("Datos del Paciente")

    genero = st.sidebar.selectbox("Género", ["Masculino", "Femenino"])
    edad_dias = st.sidebar.slider("Edad (días)", 6570, 36500, 15000)
    estatura_cm = st.sidebar.slider("Estatura (cm)", 120, 220, 170)
    peso_kg = st.sidebar.slider("Peso (kg)", 30, 200, 70)
    presion_sistolica = st.sidebar.slider("Presión Sistólica", 80, 220, 120)
    presion_diastolica = st.sidebar.slider("Presión Diastólica", 50, 150, 80)
    glucosa = st.sidebar.slider("Glucosa", 50, 300, 100)

    fuma = st.sidebar.selectbox("Fuma", ["No", "Sí"])
    alcohol = st.sidebar.selectbox("Alcohol", ["No", "Sí"])
    actividad = st.sidebar.selectbox("Actividad Física", ["Baja", "Media", "Alta"])
    colesterol = st.sidebar.selectbox("Colesterol", [1, 2, 3])

    genero = 1 if genero == "Masculino" else 0
    fuma = 1 if fuma == "Sí" else 0
    alcohol = 1 if alcohol == "Sí" else 0
    actividad = {"Baja": 0, "Media": 1, "Alta": 2}[actividad]

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
        "consume_alcohol": alcohol,
        "actividad_fisica": actividad
    }])

    st.dataframe(datos_manual, use_container_width=True, hide_index=True)

    if st.button("🔍 Predecir"):

        resultado = hacer_prediccion(datos_manual)

        if "error" in resultado:
            st.error(resultado["error"])
        else:

            fila = resultado["data"][0]
            pred = fila["prediction"]

            probs = fila.get("predictionValues", [])
            prob = max(probs, key=lambda x: x.get("value", 0)).get("value", 0)

            st.metric("Riesgo", str(pred))
            st.progress(prob)

            st.write(f"Probabilidad: {prob:.2%}")

            st.session_state.historial.append({
                "tipo": "manual",
                "prediccion": pred,
                "probabilidad": prob
            })


# ==================================
# TAB 2 - CSV
# ==================================
with tabs[1]:

    archivo = st.file_uploader("Sube CSV", type=["csv"])

    if archivo:

        df = pd.read_csv(archivo)
        st.dataframe(df.head(), hide_index=True)

        if st.button("Predecir CSV"):

            resultado = hacer_prediccion(df)

            if "error" in resultado:
                st.error(resultado["error"])
            else:

                preds = []

                for r in resultado["data"]:
                    pred = r["prediction"]
                    probs = r.get("predictionValues", [])
                    prob = max(probs, key=lambda x: x.get("value", 0)).get("value", 0)

                    preds.append(prob)

                    st.session_state.historial.append({
                        "tipo": "csv",
                        "prediccion": pred,
                        "probabilidad": prob
                    })

                df["riesgo"] = preds

                st.success("Predicciones generadas")
                st.dataframe(df, hide_index=True)

                st.download_button(
                    "Descargar",
                    df.to_csv(index=False).encode("utf-8"),
                    "resultados.csv"
                )


# ==================================
# TAB 3 - MÉTRICAS
# ==================================
with tabs[2]:

    st.subheader("📊 KPIs del modelo")

    historial = pd.DataFrame(st.session_state.historial)

    if len(historial) > 0:

        st.metric("Predicciones totales", len(historial))

        st.metric(
            "Riesgo promedio",
            f"{historial['probabilidad'].mean():.2%}"
        )

        st.metric(
            "Casos alto riesgo",
            int((historial["probabilidad"] > 0.5).sum())
        )

        st.dataframe(historial, hide_index=True)

    else:
        st.info("Aún no hay predicciones registradas")


# ==================================
# FOOTER
# ==================================
st.markdown("---")
st.caption("🩺 Dashboard PRO conectado a DataRobot | Streamlit + ML API")
