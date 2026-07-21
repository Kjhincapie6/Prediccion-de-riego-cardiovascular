"""
Modulo de prediccion local para el Predictor de Riesgo Cardiovascular.

Reemplaza la integracion con DataRobot (cuenta vencida / desactivada) por
un modelo scikit-learn entrenado localmente. El modelo va INCRUSTADO aqui
mismo como texto base64 (constante _MODEL_B64), para no depender de ningun
archivo binario ni servicio externo -- asi la app funciona con solo este
archivo de texto. No requiere API keys, deployment_id ni conexion a internet.

Entrenado con el dataset publico "Cardiovascular Disease dataset"
(70.000 registros). Accuracy ~0.74 / ROC-AUC ~0.80 en holdout del 20%.
Ver model_training/train_model.py para el detalle del entrenamiento.
"""
import base64
import io
import joblib
import pandas as pd

_MODEL_B64 = "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"

_bundle = joblib.load(io.BytesIO(base64.b64decode(_MODEL_B64)))
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
    de app.py.
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
