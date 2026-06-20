import argparse
import requests
import pandas as pd

def main():
    # ==============================
    # PARÁMETROS DE ENTRADA
    # ==============================
    parser = argparse.ArgumentParser(description="Cliente de predicciones DataRobot")
    parser.add_argument("input_file", help="Archivo CSV de entrada con datos")
    parser.add_argument("output_file", help="Archivo CSV de salida con predicciones")
    parser.add_argument("deployment_id", help="ID del deployment en DataRobot")
    parser.add_argument("--api_key", required=True, help="API key de DataRobot")
    parser.add_argument("--host", default="https://app.datarobot.com", help="Host de DataRobot")
    args = parser.parse_args()

    # ==============================
    # CONFIGURACIÓN DE LA API
    # ==============================
    headers = {
        "Authorization": f"Token {args.api_key}",   # ✅ CORRECTO: usar Token
        "Content-Type": "application/json"
    }
    url = f"{args.host}/api/v2/deployments/{args.deployment_id}/predictions"

    # ==============================
    # LECTURA DE DATOS
    # ==============================
    try:
        datos = pd.read_csv(args.input_file)
    except Exception as e:
        print(f"❌ Error leyendo el archivo de entrada: {e}")
        return

    # ==============================
    # PETICIÓN A DATAROBOT
    # ==============================
    response = requests.post(url, headers=headers, json={"data": datos.to_dict(orient="records")})

    if response.status_code != 200:
        print(f"❌ Error en la API ({response.status_code}): {response.text}")
        return

    # ==============================
    # PROCESAR RESPUESTA
    # ==============================
    resultado = response.json()
    if "data" not in resultado and "predictions" not in resultado:
        print("❌ La respuesta no contiene predicciones:", resultado)
        return

    filas = resultado.get("data", resultado.get("predictions", []))
    predicciones = []

    for fila in filas:
        if "prediction" in fila:
            predicciones.append(fila["prediction"])
        elif "predictionValues" in fila:
            predicciones.append(fila["predictionValues"][0]["value"])
        else:
            predicciones.append(None)

    # Validar longitud
    if len(predicciones) != len(datos):
        print(f"⚠️ La API devolvió {len(predicciones)} predicciones para {len(datos)} filas.")
        print("Respuesta completa:", resultado)
        return

    # ==============================
    # GUARDAR RESULTADOS
    # ==============================
    datos["prediccion"] = predicciones
    try:
        datos.to_csv(args.output_file, index=False)
        print(f"✅ Predicciones guardadas en {args.output_file}")
    except Exception as e:
        print(f"❌ Error guardando el archivo de salida: {e}")

if __name__ == "__main__":
    main()
