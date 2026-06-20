import argparse
import requests
import pandas as pd

def main():
    parser = argparse.ArgumentParser(description="Cliente de predicciones DataRobot")
    parser.add_argument("input_file", help="Archivo CSV de entrada con datos")
    parser.add_argument("output_file", help="Archivo CSV de salida con predicciones")
    parser.add_argument("deployment_id", help="ID del deployment en DataRobot")
    parser.add_argument("--api_key", required=True, help="API key de DataRobot")
    parser.add_argument("--host", default="https://app.datarobot.com", help="Host de DataRobot")
    args = parser.parse_args()

    print("🔑 API_KEY:", args.api_key[:10] + "..." if args.api_key else "VACÍO")
    print("📦 DEPLOYMENT_ID:", args.deployment_id)
    print("🌐 HOST:", args.host)

    headers = {
        "Authorization": f"Token {args.api_key}",   # ✅ CORRECTO
        "Content-Type": "application/json"
    }
    url = f"{args.host}/api/v2/deployments/{args.deployment_id}/predictions"

    try:
        datos = pd.read_csv(args.input_file)
    except Exception as e:
        print(f"❌ Error leyendo el archivo de entrada: {e}")
        return

    response = requests.post(url, headers=headers, json={"data": datos.to_dict(orient="records")})

    if response.status_code != 200:
        print(f"❌ Error en la API ({response.status_code}): {response.text}")
        return

    resultado = response.json()
    filas = resultado.get("data", resultado.get("predictions", []))
    predicciones = []

    for fila in filas:
        if "prediction" in fila:
            predicciones.append(fila["prediction"])
        elif "predictionValues" in fila:
            predicciones.append(fila["predictionValues"][0]["value"])
        else:
            predicciones.append(None)

    if len(predicciones) != len(datos):
        print(f"⚠️ La API devolvió {len(predicciones)} predicciones para {len(datos)} filas.")
        print("Respuesta completa:", resultado)
        return

    datos["prediccion"] = predicciones
    try:
        datos.to_csv(args.output_file, index=False)
        print(f"✅ Predicciones guardadas en {args.output_file}")
    except Exception as e:
        print(f"❌ Error guardando el archivo de salida: {e}")

if __name__ == "__main__":
    main()

