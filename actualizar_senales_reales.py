import pandas as pd
import numpy as np

# === Cargar archivo original ===
archivo = "Senales_emitidas_registradas.csv"

df = pd.read_csv(archivo)
df.columns = df.columns.str.lower()

# === Crear columnas necesarias ===
# Usar 'precio_entrada' como 'close' si no hay 'close'
if "close" not in df.columns and "precio_entrada" in df.columns:
    df["close"] = df["precio_entrada"]
if "high" not in df.columns:
    df["high"] = df["close"]
if "low" not in df.columns:
    df["low"] = df["close"]

# === Calcular indicadores técnicos ===

# EMA 35 y 50
df["ema_35"] = df["close"].ewm(span=35, adjust=False).mean()
df["ema_50"] = df["close"].ewm(span=50, adjust=False).mean()

# RSI
delta = df["close"].diff()
ganancia = delta.where(delta > 0, 0)
perdida = -delta.where(delta < 0, 0)
avg_ganancia = ganancia.ewm(alpha=1/14, adjust=False).mean()
avg_perdida = perdida.ewm(alpha=1/14, adjust=False).mean()
rs = avg_ganancia / avg_perdida
df["rsi"] = 100 - (100 / (1 + rs))

# ADX
plus_dm = df["high"].diff()
minus_dm = -df["low"].diff()
plus_dm[plus_dm < 0] = 0
minus_dm[minus_dm < 0] = 0

tr_components = pd.DataFrame({
    'hl': df['high'] - df['low'],
    'hc': abs(df['high'] - df['close'].shift()),
    'lc': abs(df['low'] - df['close'].shift())
})
tr = tr_components.max(axis=1)
atr = tr.rolling(window=14).mean()

plus_di = 100 * (plus_dm.rolling(window=14).mean() / atr)
minus_di = 100 * (minus_dm.rolling(window=14).mean() / atr)
dx = (abs(plus_di - minus_di) / (plus_di + minus_di)) * 100
df["adx"] = dx.rolling(window=14).mean()

# === Limpiar NaN finales ===
df.dropna(subset=["ema_35", "ema_50", "rsi", "adx", "resultado"], inplace=True)

# === Sobrescribir archivo original ===
df.to_csv(archivo, index=False)
print(f"✅ Archivo actualizado con indicadores guardado como: {archivo}")
