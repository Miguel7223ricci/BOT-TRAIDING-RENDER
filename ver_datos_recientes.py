from data_providers import obtener_datos
from config_activos import CONFIG
import pandas as pd

# Elegir un activo cualquiera (puedes cambiarlo por el que quieras probar)
nombre = "EURCAD"
ticker = CONFIG["activos"][nombre]

# Obtener datos
df = obtener_datos(ticker, CONFIG["intervalo"], CONFIG["periodo"])

if df is not None and not df.empty:
    print(f"\n🕒 Última fecha disponible para {nombre}: {df.index[-1]}")
    print("\n📊 Últimas 5 velas:")
    print(df.tail(5))
else:
    print(f"❌ No se obtuvieron datos para {nombre}")
