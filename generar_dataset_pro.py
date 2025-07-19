
# generar_dataset_pro.py con Alpaca

import os
import pandas as pd
from indicadores_tecnicos import calcular_indicadores
from data_providers import obtener_datos
from config_activos import CONFIG

os.makedirs("datasets", exist_ok=True)
dataset_final = []

for nombre, ticker in CONFIG["activos"].items():
    print(f"📥 Descargando {nombre} ({ticker})...")
    df = obtener_datos(ticker, CONFIG["intervalo"], CONFIG["periodo"])

    if df is None or len(df) < 100:
        print(f"⚠️ Datos insuficientes para {nombre}")
        continue

    df = calcular_indicadores(df)
    df.dropna(inplace=True)
    if df.empty:
        continue

    df['Activo'] = nombre
    df['Datetime'] = df.index
    dataset_final.append(df)

# Concatenar y guardar
if dataset_final:
    dataset = pd.concat(dataset_final)
    dataset.to_csv("datasets/dataset_entrenamiento_pro.csv", index=False)
    print(f"✅ Dataset guardado: datasets/dataset_entrenamiento_pro.csv (filas: {len(dataset)})")
else:
    print("❌ No se pudo generar el dataset. Verifica tus claves o tickers.")
