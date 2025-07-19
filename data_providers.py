# data_providers.py

import os
import requests
import pandas as pd
import logging
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

    # Calcular fecha de inicio
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
            logger.error(f"❌ Error al obtener datos de {ticker}: {data.get('message')}")
            return None

        valores = data.get("values", [])
        if not valores:
            logger.warning(f"⚠️ Sin datos para {ticker}")
            return None

        df = pd.DataFrame(valores)

        # Normalizar nombres de columnas
        df.columns = [col.lower() for col in df.columns]

        # Renombrar a formato con mayúsculas iniciales
        columnas_objetivo = {
            "open": "Open", "high": "High", "low": "Low", "close": "Close", "volume": "Volume", "datetime": "Datetime"
        }
        df.rename(columns={k: v for k, v in columnas_objetivo.items() if k in df.columns}, inplace=True)

        logger.info(f"📊 Columnas recibidas para {ticker}: {df.columns.tolist()}")
        if "Close" not in df.columns:
            logger.warning(f"⚠️ 'Close' no disponible en datos para {ticker}. Generando con promedio OHLC")
            if all(col in df.columns for col in ["Open", "High", "Low"]):
                df["Close"] = df[["Open", "High", "Low"]].astype(float).mean(axis=1)
            else:
                logger.error(f"❌ No se puede crear 'Close' por falta de columnas OHLC en {ticker}")
                return None

        # Parsear fecha y ordenar
        df["Datetime"] = pd.to_datetime(df["Datetime"])
        df.set_index("Datetime", inplace=True)
        df = df.sort_index()

        # Convertir a float
        for col in ["Open", "High", "Low", "Close", "Volume"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        df.dropna(inplace=True)
        logger.info(f"✅ Datos obtenidos para {ticker} ({len(df)} registros)")

        return df

    except Exception as e:
        logger.exception(f"❌ Excepción al obtener datos de {ticker}: {e}")
        return None

