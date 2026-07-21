"""
Modulo de prediccion local para el Predictor de Riesgo Cardiovascular.

Reemplaza la integracion con DataRobot (cuenta vencida / desactivada) por
un modelo scikit-learn (RandomForestClassifier) entrenado localmente y
empaquetado en model.pkl (archivo binario, subido directamente al repo).
No requiere API keys, deployment_id ni conexion a ningun servicio externo
-- el modelo corre dentro de la misma app.

Entrenado con el dataset publico "Cardiovascular Disease dataset"
(70.000 registros). Accuracy ~0.74 / ROC-AUC ~0.80 en holdout del 20%.
Ver model_training/train_model.py para el detalle del entrenamiento.
"""
import os
import joblib
import pandas as pd

_MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "model.pkl")

_bundle = joblib.load(_MODEL_PATH)
_model = _bundle["model"]
_FEATURE_ORDER = _bundle["feature_order"]


def _categorizar_glucosa(valor_mgdl):
    """
    La app recoge la glucosa como un valor continuo en mg/dL (slider),
    pero el modelo fue entrenado con la escala categorica del dataset
    original (igual que 'colesterol'):
        1 = Normal                    (< 100 mg/dL)
        2 = Por encima de lo normal   (100-125 mg/dL)
        3 = Muy superior a lo normal  (> 125 mg/dL)
    Umbrales basados en criterios clinicos estandar de glucosa en ayunas.
    """
    if valor_mgdl < 100:
        return 1
    elif valor_mgdl <= 125:
        return 2
    return 3


def _binarizar_actividad(nivel):
    """
    La app recoge actividad fisica como Baja/Media/Alta (0/1/2), pero el
    modelo fue entrenado con la variable binaria original del dataset
    (activo/inactivo). Se considera activo (1) cualquier nivel Media o Alta.
    """
    return 0 if nivel == 0 else 1


def predecir(df: pd.DataFrame) -> dict:
    """
    Recibe un DataFrame con columnas en ingles (age, gender, height, weight,
    ap_hi, ap_lo, cholesterol, gluc, smoke, alco, active) -- el mismo formato
    que antes se enviaba a la API de DataRobot -- y devuelve un dict con la
    MISMA estructura que devolvia esa API, para no tener que tocar el resto
    de app.py:

        {
          "data": [
            {
              "prediction": 0 | 1,
              "predictionValues": [
                {"label": 0, "value": prob_sin_riesgo},
                {"label": 1, "value": prob_con_riesgo},
              ],
            },
            ...
          ]
        }
    """
    datos = df.copy()

    columnas_requeridas = ["age", "gender", "height", "weight", "ap_hi", "ap_lo",
                            "cholesterol", "gluc", "smoke", "alco", "active"]
    faltantes = [c for c in columnas_requeridas if c not in datos.columns]
    if faltantes:
        raise ValueError(f"Faltan columnas requeridas para la prediccion: {faltantes}")

    datos["gluc"] = datos["gluc"].apply(_categorizar_glucosa)
    datos["active"] = datos["active"].apply(_binarizar_actividad)

    X = datos[_FEATURE_ORDER]

    predicciones = _model.predict(X)
    probabilidades = _model.predict_proba(X)

    resultados = []
    for pred, probs in zip(predicciones, probabilidades):
        resultados.append({
            "prediction": int(pred),
            "predictionValues": [
                {"label": 0, "value": float(probs[0])},
                {"label": 1, "value": float(probs[1])},
            ],
        })

    return {"data": resultados}
