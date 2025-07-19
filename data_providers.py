# data_providers.py

import os
import requests
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()
API_KEY = os.getenv("TWELVE_DATA_API_KEY")

def obtener_datos(ticker, intervalo="4h", periodo="60d"):
    """Obtiene datos históricos de Twelve Data para el símbolo dado."""

    if not API_KEY:
        print("❌ TWELVE_DATA_API_KEY no configurada en .env")
        return None

    # Convertir '60d' a fecha de inicio
    hoy = datetime.utcnow()
    dias = int(periodo.replace("d", ""))
    fecha_inicio = hoy - timedelta(days=dias)

    url = "https://api.twelvedata.com/time_series"
    params = {
        "symbol": ticker,
        "interval": intervalo,
        "start_date": fecha_inicio.strftime("%Y-%m-%d"),
        "end_date": hoy.strftime("%Y-%m-%d"),
        "apikey": API_KEY,
        "format": "JSON",
        "outputsize": 5000
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()

        if "status" in data and data["status"] == "error":
            print(f"❌ Error al obtener datos de {ticker}: {data.get('message')}")
            return None

        valores = data.get("values", [])
        if not valores:
            print(f"⚠️ Sin datos para {ticker}")
            return None

	df = pd.DataFrame(valores)
	df.columns = [col.upper() for col in df.columns]  # Convertir columnas a mayúsculas
	df["DATETIME"] = pd.to_datetime(df["DATETIME"])
	df.set_index("DATETIME", inplace=True)

	df = df.astype(float)
	df = df.sort_index()
	return df

    except Exception as e:
        print(f"❌ Excepción al obtener datos de {ticker}: {e}")
        return None
