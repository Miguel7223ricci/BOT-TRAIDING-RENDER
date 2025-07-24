import requests
import pandas as pd
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# === 1. Cargar API Key desde archivo .env ===
load_dotenv()
TWELVE_DATA_API_KEY = os.getenv("TWELVE_DATA_API_KEY")

# === 2. Activos en formato símbolo Twelve Data ===
activos = [
    "EUR/USD",
]

# === 3. Definir fechas de inicio y fin (últimos 5 días)
hoy = datetime.utcnow()
inicio = hoy - timedelta(days=5)

# === 4. Función para consultar datos por símbolo ===
def obtener_datos_twelvedata(symbol):
    url = "https://api.twelvedata.com/time_series"
    params = {
        "symbol": symbol,
        "interval": "1h",
        "apikey": TWELVE_DATA_API_KEY,
        "start_date": inicio.strftime("%Y-%m-%d"),
        "end_date": hoy.strftime("%Y-%m-%d"),
        "format": "JSON",
        "outputsize": 5000
    }

    try:
        r = requests.get(url, params=params)
        data = r.json()

        if "status" in data and data["status"] == "error":
            return (symbol, 0, f"Error: {data.get('message', 'desconocido')}")

        values = data.get("values", [])
        if not values:
            return (symbol, 0, "Sin datos")

        fechas = [v["datetime"] for v in values]
        ultima_fecha = fechas[0]  # Twelve Data ordena descendente
        return (symbol, len(fechas), ultima_fecha)

    except Exception as e:
        return (symbol, 0, f"Excepción: {str(e)}")

# === 5. Ejecutar para todos los activos ===
resultados = [obtener_datos_twelvedata(sym) for sym in activos]

# === 6. Mostrar y guardar ===
df = pd.DataFrame(resultados, columns=["Activo", "Cantidad de velas 1H", "Última vela disponible"])
print(df)

df.to_csv("resultados_twelvedata.csv", index=False)
print("\n✅ Resultados guardados como 'resultados_twelvedata.csv'")
