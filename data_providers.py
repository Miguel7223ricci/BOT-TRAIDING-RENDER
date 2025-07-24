# data_providers.py

import os
import requests
import pandas as pd
import logging
import urllib.parse
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()
API_KEY = os.getenv("TWELVE_DATA_API_KEY")

logger = logging.getLogger(__name__)

def obtener_datos(ticker, intervalo="4h", periodo="60d"):
    """Obtiene datos históricos de Twelve Data para el símbolo dado."""
    if not API_KEY:
        logger.error("❌ TWELVE_DATA_API_KEY no configurada en .env")
        return None

    hoy = datetime.utcnow()
    dias = int(periodo.replace("d", ""))
    fecha_inicio = hoy - timedelta(days=dias)

    # Codificar el símbolo para que funcione con símbolos como EUR/USD
    symbol_codificado = urllib.parse.quote(ticker)

    url = "https://api.twelvedata.com/time_series"
    params = {
        "symbol": symbol_codificado,
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
            logger.error(f"❌ Error al obtener datos de {ticker}: {data.get('message')}")
            return None

        valores = data.get("values", [])
        if not valores:
            logger.warning(f"⚠️ Sin datos para {ticker}")
            return None

        df = pd.DataFrame(valores)
        df.columns = [col.lower() for col in df.columns]

        logger.info(f"📊 Columnas recibidas para {ticker}: {df.columns.tolist()}")

        if "close" not in df.columns:
            logger.warning(f"⚠️ 'close' no disponible. Estimando como promedio OHLC")
            if all(col in df.columns for col in ["open", "high", "low"]):
                df["close"] = df[["open", "high", "low"]].astype(float).mean(axis=1)
            else:
                logger.error(f"❌ Faltan columnas para generar 'close' en {ticker}")
                return None

        df["datetime"] = pd.to_datetime(df["datetime"])
        df.set_index("datetime", inplace=True)
        df = df.sort_index()

        for col in ["open", "high", "low", "close", "volume"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        df.dropna(inplace=True)
        logger.info(f"✅ Datos obtenidos para {ticker} ({len(df)} registros)")

        return df

    except Exception as e:
        logger.exception(f"❌ Excepción al obtener datos de {ticker}: {e}")
        return None
