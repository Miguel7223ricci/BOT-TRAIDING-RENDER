import requests
import pandas as pd
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# === 1. Cargar API Key desde .env ===
load_dotenv()
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")

# === 2. Lista de activos (códigos según Finnhub) ===
activos = [
   
    "EURUSD",                 # Forex
]

# === 3. Fechas de inicio y fin (últimos 5 días) ===
hoy = datetime.utcnow()
inicio = hoy - timedelta(days=5)

# === 4. Convertir fechas a timestamp UNIX ===
inicio_unix = int(inicio.timestamp())
fin_unix = int(hoy.timestamp())

# === 5. Función para obtener y analizar datos por activo ===
def obtener_datos(symbol):
    url = "https://finnhub.io/api/v1/stock/candle"
    params = {
        "symbol": symbol,
        "resolution": "60",  # 60 minutos = 1h
        "from": inicio_unix,
        "to": fin_unix,
        "token": FINNHUB_API_KEY
    }

    try:
        r = requests.get(url, params=params)
        data = r.json()

        if data.get("s") != "ok":
            return (symbol, 0, f"Error: {data.get('s', 'sin respuesta')}")

        timestamps = data.get("t", [])
        if not timestamps:
            return (symbol, 0, "Sin datos")

        ultima = datetime.utcfromtimestamp(timestamps[-1])
        return (symbol, len(timestamps), ultima)

    except Exception as e:
        return (symbol, 0, f"Excepción: {str(e)}")

# === 6. Ejecutar para todos los activos y guardar resultados ===
resultados = [obtener_datos(symbol) for symbol in activos]

# === 7. Mostrar resultados como tabla ===
df = pd.DataFrame(resultados, columns=["Activo", "Cantidad de velas 1H", "Última vela disponible"])
print(df)

# === 8. (Opcional) Guardar como CSV ===
df.to_csv("resultados_finnhub.csv", index=False)
print("\n✅ Resultados guardados en 'resultados_finnhub.csv'")


