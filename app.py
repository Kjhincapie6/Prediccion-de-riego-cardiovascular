import streamlit as st
import pandas as pd
import subprocess
import os

st.title("Predicción de riesgo cardiovascular")

# --- Formulario de entrada ---
edad = st.number_input("Edad en años", min_value=1, max_value=120, value=50)
genero = st.selectbox("Género", [0, 1])  # 0 = mujer, 1 = hombre
estatura = st.number_input("Estatura en cm", min_value=100, max_value=220, value=170)
peso = st.number_input("Peso en kg", min_value=30.0, max_value=200.0, value=70.0)
presion_sistolica = st.number_input("Presión sistólica", min_value=80, max_value=200, value=120)
presion_diastolica = st.number_input("Presión diastólica", min_value=50, max_value=130, value=80)
colesterol = st.selectbox("Colesterol", [1, 2, 3])  # 1=Normal, 2=Arriba de lo normal, 3=Muy alto
glucosa = st.selectbox("Glucosa", [1, 2, 3])       # 1=Normal, 2=Arriba de lo normal, 3=Muy alto
fuma = st.selectbox("¿Fuma?", ["No", "Sí"])
alcohol = st.selectbox("¿Consume alcohol?", ["No", "Sí"])
actividad = st.selectbox("¿Realiza actividad física?", ["No", "Sí"])

# --- Variable calculada: IMC ---
imc = round(peso / ((estatura / 100) ** 2), 2)
st.write("Índice de masa corporal:", imc)

# --- Botón de predicción ---
if st.button("Predecir riesgo cardiovascular"):
    # Crear CSV temporal con los datos del formulario
    df = pd.DataFrame([{
        "age": edad,
        "gender": genero,
        "height": estatura,
        "weight": peso,
        "ap_hi": presion_sistolica,
        "ap_lo": presion_diastolica,
        "cholesterol": colesterol,
        "gluc": glucosa,
        "smoke": 1 if fuma == "Sí" else 0,
        "alco": 1 if alcohol == "Sí" else 0,
        "active": 1 if actividad == "Sí" else 0
    }])
    df.to_csv("temp_input.csv", index=False)

    # Ejecutar predict.py con el CSV temporal
    try:
        subprocess.run([
            "python",
            "C:/Users/kelly/OneDrive/Documentos/EstudIA/DATAROBOT/PREDICCIONES CARDIO/predict.py",
            "temp_input.csv",
            "temp_output.csv",
            "6a35a3e185191304741588d4",
            "--api_key=TU_API_KEY_REAL",
            "--host=https://app.datarobot.com"
        ], check=True)

        # Leer resultados y mostrarlos
        if os.path.exists("temp_output.csv"):
            resultados = pd.read_csv("temp_output.csv")
            st.success("Predicción realizada con éxito")
            st.write(resultados)
        else:
            st.error("No se generó el archivo de resultados.")
    except Exception as e:
        st.error(f"Error ejecutando predict.py: {e}")
