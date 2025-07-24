# generar_dataset_pro.py
# Descarga datos desde Twelve Data y guarda un CSV por activo. Luego los concatena.

import os
import time
import pandas as pd
from indicadores_tecnicos import calcular_indicadores
from data_providers import obtener_datos
from config_activos import CONFIG

os.makedirs("datasets", exist_ok=True)
archivos_guardados = []

for nombre, ticker in CONFIG["activos"].items():
    print(f"📥 Descargando {nombre} ({ticker})...")
    try:
        df = obtener_datos(ticker, CONFIG["intervalo"], CONFIG["periodo"])

        if df is None or len(df) < 100:
            print(f"⚠️ Datos insuficientes para {nombre}")
            continue

        df = calcular_indicadores(df)
        df.dropna(inplace=True)
        if df.empty:
            continue

        df["Activo"] = nombre
        df["Datetime"] = df.index

        nombre_archivo = f"datasets/{nombre.replace(' ', '_')}_{ticker.replace('/', '')}.csv"
        df.to_csv(nombre_archivo, index=False)
        archivos_guardados.append(nombre_archivo)
        print(f"✅ Guardado: {nombre_archivo} ({len(df)} filas)")

    except Exception as e:
        print(f"❌ Error en {nombre}: {e}")

    time.sleep(8)  # Control de uso API gratuita

# Concatenar todo en un solo archivo final
if archivos_guardados:
    dataframes = [pd.read_csv(archivo) for archivo in archivos_guardados]
    dataset_total = pd.concat(dataframes)
    dataset_total.to_csv("datasets/dataset_entrenamiento_pro.csv", index=False)
    print(f"\n✅ Dataset final guardado con {len(dataset_total)} filas.")
else:
    print("❌ No se pudo generar el dataset. Ningún activo fue guardado.")

