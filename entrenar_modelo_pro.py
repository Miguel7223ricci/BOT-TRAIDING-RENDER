import pandas as pd
import numpy as np
from ta.trend import EMAIndicator
from ta.volatility import AverageTrueRange
from ta.momentum import RSIIndicator
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import joblib

# === 1. Cargar dataset ===
df = pd.read_csv("dataset_entrenamiento_pro.csv")
df.columns = df.columns.str.lower()  # Asegura nombres en minúsculas

# Asegura que existan las columnas necesarias
for col in ["open", "high", "low", "close"]:
    if col not in df.columns:
        raise ValueError(f"Falta la columna {col} en el archivo CSV.")

# === 2. Calcular indicadores técnicos ===
df["ema_rapida"] = EMAIndicator(close=df["close"], window=21).ema_indicator()
df["ema_lenta"] = EMAIndicator(close=df["close"], window=50).ema_indicator()
df["atr"] = AverageTrueRange(high=df["high"], low=df["low"], close=df["close"], window=14).average_true_range()
df["rsi"] = RSIIndicator(close=df["close"], window=14).rsi()

# === 3. Crear columna objetivo ===
# Si el precio sube en los próximos 3 pasos → GANANCIA, sino → PERDIDA
df["future_close"] = df["close"].shift(-3)
df["direccion"] = np.where(df["future_close"] > df["close"], "GANANCIA", "PERDIDA")

# Elimina filas con NaN (por indicadores o shift)
df.dropna(inplace=True)

# === 4. Selección de variables ===
features = ["atr", "ema_rapida", "ema_lenta", "rsi"]
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

# === 8. Guardar dataset procesado (opcional) ===
df.to_csv("dataset_entrenamiento_actualizado.csv", index=False)
print("📁 Dataset actualizado guardado como dataset_entrenamiento_actualizado.csv")
