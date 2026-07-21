
import sys
import os
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, roc_auc_score, classification_report
import joblib

RANDOM_STATE = 42
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    dataset_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(REPO_ROOT, "cardio_train.csv")
    if not os.path.exists(dataset_path):
        print(f"No se encontro el dataset en: {dataset_path}")
        print("Descargalo desde https://www.kaggle.com/datasets/sulianova/cardiovascular-disease-dataset")
        print("y pasa la ruta como argumento: python model_training/train_model.py ruta/cardio_train.csv")
        sys.exit(1)

    print("Cargando dataset...")
    df = pd.read_csv(dataset_path, sep=";")
    print(f"Filas originales: {len(df)}")

    # -----------------------------------------------------------
    # Limpieza: eliminar registros fisiologicamente imposibles/erroneos
    # (practica estandar y documentada para este dataset)
    # -----------------------------------------------------------
    df = df[(df["height"] >= 130) & (df["height"] <= 220)]
    df = df[(df["weight"] >= 30) & (df["weight"] <= 200)]
    df = df[(df["ap_hi"] >= 80) & (df["ap_hi"] <= 220)]
    df = df[(df["ap_lo"] >= 50) & (df["ap_lo"] <= 150)]
    df = df[df["ap_hi"] > df["ap_lo"]]
    print(f"Filas tras limpieza: {len(df)}")

    # -----------------------------------------------------------
    # Remapeo de genero para que coincida con la codificacion de la app
    # -----------------------------------------------------------
    df["gender"] = np.where(df["gender"] == 2, 1, 0)  # 2=hombre->1, 1=mujer->0

    feature_cols = ["age", "gender", "height", "weight", "ap_hi", "ap_lo",
                     "cholesterol", "gluc", "smoke", "alco", "active"]

    X = df[feature_cols]
    y = df["cardio"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y
    )

    print("Entrenando RandomForestClassifier...")
    model = RandomForestClassifier(
        n_estimators=150,
        max_depth=8,
        min_samples_leaf=25,
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    acc = accuracy_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_proba)
    print(f"\nAccuracy: {acc:.4f}")
    print(f"ROC-AUC: {auc:.4f}")
    print("\n" + classification_report(y_test, y_pred, target_names=["Sin riesgo", "Con riesgo"]))

    output_path = os.path.join(REPO_ROOT, "model.pkl")
    joblib.dump({"model": model, "feature_order": feature_cols}, output_path)
    print(f"\nModelo guardado en {output_path}")


if __name__ == "__main__":
    main()
