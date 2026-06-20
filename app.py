import pandas as pd
import subprocess

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
    "smoke": fuma,
    "alco": alcohol,
    "active": actividad
}])
df.to_csv("temp_input.csv", index=False)

# Llamar a predict.py con ese CSV
subprocess.run([
    "python",
    "C:/Users/kelly/OneDrive/Documentos/EstudIA/DATAROBOT/PREDICCIONES CARDIO/predict.py",
    "temp_input.csv",
    "temp_output.csv",
    "6a35a3e185191304741588d4",
    "--api_key=TU_API_KEY_REAL",
    "--host=https://app.datarobot.com"
])
