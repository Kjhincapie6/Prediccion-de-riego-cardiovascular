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

endpoint = f"{HOST}/predApi/v1.0/deployments/{DEPLOYMENT_ID}/predictions"

# ==================================
# FUNCIÓN DE PREDICCIÓN
# ==================================
def hacer_prediccion(payload):
    try:
        response = requests.post(endpoint, json=payload, headers=headers)

        # DEBUG OCULTO
        with st.expander("🔧 Información técnica"):
            st.code(f"STATUS: {response.status_code}")
            try:
                st.json(response.json())
            except Exception:
                st.text(response.text)

        if response.status_code != 200:
            st.error("Error en la API de DataRobot")
            return None, None

        data = response.json()

        # Ajusta según respuesta real de DataRobot
        pred = data.get("prediction", None)
        prob_riesgo = data.get("probability", None)

        # Normalización segura (si viene en porcentaje)
        if prob_riesgo is not None and prob_riesgo > 1:
            prob_riesgo = prob_riesgo / 100

        return pred, prob_riesgo

    except Exception as e:
        st.error(f"Error en la solicitud: {e}")
        return None, None


# ==================================
# INTERFAZ
# ==================================
st.title("🫀 Predicción de Riesgo Cardiovascular")

# ==============================
# INPUT MANUAL
# ==============================
st.header("Ingreso Manual de Datos")

edad = st.number_input("Edad en años", 1, 120, 50)
genero = st.selectbox("Género", [0, 1])
estatura = st.number_input("Estatura (cm)", 100, 220, 170)
peso = st.number_input("Peso (kg)", 30, 200, 70)
sistolica = st.number_input("Presión sistólica", 80, 200, 120)
diastolica = st.number_input("Presión diastólica", 40, 130, 80)
colesterol = st.selectbox("Colesterol", [1, 2, 3])
glucosa = st.selectbox("Glucosa", [1, 2, 3])
fuma = st.selectbox("Fuma", [0, 1])
alcohol = st.selectbox("Consume alcohol", [0, 1])

if st.button("Predecir riesgo manual"):
    payload = {
        "edad_dias": edad,
        "genero": genero,
        "estatura_cm": estatura,
        "peso_kg": peso,
        "presion_sistolica": sistolica,
        "presion_diastolica": diastolica,
        "colesterol": colesterol,
        "glucosa": glucosa,
        "fuma": fuma,
        "alcohol": alcohol
    }

    pred, prob_riesgo = hacer_prediccion(payload)

    if pred is not None:

        st.subheader("🩺 Resultado del modelo")

        if pred == 1:
            st.markdown(
                """
                <div style="
                    background-color:#FDEDEC;
                    padding:20px;
                    border-radius:12px;
                    border-left:8px solid #E74C3C;
                    margin-bottom:15px;
                ">
                    <h3>🔴 Alto Riesgo Cardiovascular</h3>
                    <p>El modelo identifica una probabilidad elevada de enfermedad cardiovascular.</p>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                """
                <div style="
                    background-color:#EAFAF1;
                    padding:20px;
                    border-radius:12px;
                    border-left:8px solid #28B463;
                    margin-bottom:15px;
                ">
                    <h3>🟢 Bajo Riesgo Cardiovascular</h3>
                    <p>El modelo identifica una probabilidad baja de enfermedad cardiovascular.</p>
                </div>
                """,
                unsafe_allow_html=True
            )

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Clase de Riesgo", str(pred))

        with col2:
            if prob_riesgo is not None:
                st.metric("Probabilidad", f"{prob_riesgo:.2%}")

        if prob_riesgo is not None:
            st.progress(float(prob_riesgo))

            if prob_riesgo >= 0.80:
                st.error("⚠️ Riesgo muy elevado")
            elif prob_riesgo >= 0.50:
                st.warning("⚠️ Riesgo moderado")
            else:
                st.success("✅ Riesgo bajo")


# ==============================
# INPUT CSV
# ==============================
st.header("Carga de archivo CSV")

archivo = st.file_uploader("Sube tu archivo CSV", type=["csv"])

if archivo is not None:
    datos_csv = pd.read_csv(archivo)
    st.dataframe(
        datos_csv.head(),
        use_container_width=True,
        hide_index=True
    )

    if st.button("Predecir CSV"):
        resultados = []

        for _, fila in datos_csv.iterrows():
            payload = fila.to_dict()
            pred, prob = hacer_prediccion(payload)

            resultados.append({
                "prediccion": pred,
                "probabilidad": prob
            })

        df_resultados = pd.DataFrame(resultados)

        st.subheader("Resultados CSV")

        st.dataframe(
            df_resultados,
            use_container_width=True,
            hide_index=True
        )
