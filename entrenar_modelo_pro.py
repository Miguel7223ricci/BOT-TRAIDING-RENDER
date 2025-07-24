import pandas as pd
import numpy as np
from ta.trend import EMAIndicator, ADXIndicator
from ta.momentum import RSIIndicator
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import joblib

# === 1. Cargar dataset ===
df = pd.read_csv("dataset_entrenamiento_pro.csv")
df.columns = df.columns.str.lower()

# Verificar columnas necesarias
for col in ["open", "high", "low", "close"]:
    if col not in df.columns:
        raise ValueError(f"❌ Falta la columna requerida: {col}")

# === 2. Calcular indicadores técnicos actualizados ===
df["ema_35"] = EMAIndicator(close=df["close"], window=35).ema_indicator()
df["ema_50"] = EMAIndicator(close=df["close"], window=50).ema_indicator()
df["rsi"] = RSIIndicator(close=df["close"], window=14).rsi()
df["adx"] = ADXIndicator(high=df["high"], low=df["low"], close=df["close"], window=14).adx()

# === 3. Crear columna objetivo con clases BUY / SELL ===
df["future_close"] = df["close"].shift(-3)
df["direccion"] = np.where(df["future_close"] > df["close"], "BUY", "SELL")

df.dropna(inplace=True)

# === 4. Selección de variables ===
features = ["ema_35", "ema_50", "rsi", "adx"]
X = df[features]
y = df["direccion"]

# === 5. División entrenamiento / test ===
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# === 6. Entrenar modelo ===
modelo = RandomForestClassifier(n_estimators=100, random_state=42)
modelo.fit(X_train, y_train)
print("✅ Modelo entrenado con éxito")

# === 7. Guardar modelo ===
joblib.dump(modelo, "modelo_trained_rf_pro.pkl")
print("💾 Modelo guardado como modelo_trained_rf_pro.pkl")

# === 8. Guardar dataset actualizado
df.to_csv("dataset_entrenamiento_actualizado.csv", index=False)
print("📁 Dataset actualizado guardado como dataset_entrenamiento_actualizado.csv")



