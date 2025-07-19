# entrenar_modelo_pro.py

import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# ============================== CONFIGURACIÓN ==============================
RUTA_SALIDA_MODELO = "modelo_trained_rf_pro.pkl"
UMBRAL_RETORNO = 0.0025  # 0.25%
VENTANA_RETARDO = 6  # 6 velas = 24h en intervalo 4h

# ============================== FUNCIONES ==============================

def calcular_etiquetas(df):
    """Crea la columna de etiquetas (BUY, SELL, HOLD) según variación futura del precio"""
    df = df.copy()
    df["future_return"] = df["CLOSE"].shift(-VENTANA_RETARDO) / df["CLOSE"] - 1
    condiciones = [
        df["future_return"] > UMBRAL_RETORNO,
        df["future_return"] < -UMBRAL_RETORNO
    ]
    elecciones = ["BUY", "SELL"]
    df["Label"] = np.select(condiciones, elecciones, default="HOLD")
    return df.dropna()

def cargar_dataset(csv_path):
    df = pd.read_csv(csv_path, parse_dates=["Datetime"])
    df.columns = [col.upper() for col in df.columns]
    df.set_index("DATETIME", inplace=True)
    df.dropna(inplace=True)
    return df

def entrenar_modelo(df):
    """Entrena el modelo RandomForest con los datos disponibles"""
    df = calcular_etiquetas(df)

    # Usar las columnas disponibles en tu CSV como features
    columnas_features = ["H-L", "O-C", "MA10", "MA50", "STDDEV"]

    X = df[columnas_features]
    y = df["Label"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, stratify=y, test_size=0.2, random_state=42)

    modelo = RandomForestClassifier(n_estimators=200, max_depth=6, class_weight="balanced", random_state=42)
    modelo.fit(X_train, y_train)

    y_pred = modelo.predict(X_test)
    print("\n====== CLASIFICACIÓN ======")
    print(classification_report(y_test, y_pred))

    return modelo

# ============================== FLUJO PRINCIPAL ==============================

def main():
    csv_path = "datasets/dataset_entrenamiento_pro.csv"  # Asegúrate de que exista
    df = cargar_dataset(csv_path)
    modelo = entrenar_modelo(df)
    joblib.dump(modelo, RUTA_SALIDA_MODELO)
    print(f"\n✅ Modelo guardado en: {RUTA_SALIDA_MODELO}")

if __name__ == "__main__":
    main()

