# data_providers.py

import os
import time
import requests
import pandas as pd
import logging
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()
API_KEY = os.getenv("TWELVE_DATA_API_KEY")
logger = logging.getLogger(__name__)

def obtener_datos(ticker, intervalo="4h", periodo="60d", max_intentos=3):
    """Obtiene datos históricos de Twelve Data para el símbolo dado."""

    if not API_KEY:
        logger.error("❌ TWELVE_DATA_API_KEY no configurada en .env")
        return None

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

    for intento in range(1, max_intentos + 1):
        logger.info(f"🔍 Evaluando {ticker} [Intento {intento}]")

        try:
            response = requests.get(url, params=params)
            data = response.json()

            if "status" in data and data["status"] == "error":
                mensaje = data.get("message", "")
                logger.error(f"❌ Error API para {ticker}: {mensaje}")

                if "API credits" in mensaje:
                    logger.info("⏳ Límite de créditos alcanzado, esperando 60 segundos...")
                    time.sleep(60)
                    return None

                return None

            valores = data.get("values", [])
            if not valores:
                logger.warning(f"⚠️ Sin datos disponibles para {ticker}")
                return None

            df = pd.DataFrame(valores)
            logger.info(f"📊 Columnas recibidas para {ticker}: {df.columns.tolist()}")

            # Renombrar columnas a formato esperado
            df.columns = [col.lower() for col in df.columns]
            column_mapping = {
                'close': 'Close',
                'closing': 'Close',
                'price': 'Close',
                'value': 'Close',
                'datetime': 'datetime',
                'date': 'datetime',
                'time': 'datetime'
            }
            df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns}, inplace=True)

            if "Close" not in df.columns:
                if all(col in df.columns for col in ['open', 'high', 'low']):
                    logger.warning(f"⚠️ Generando 'Close' como promedio OHLC para {ticker}")
                    df['Close'] = (pd.to_numeric(df['open'], errors='coerce') +
                                   pd.to_numeric(df['high'], errors='coerce') +
                                   pd.to_numeric(df['low'], errors='coerce')) / 3
                else:
                    logger.error(f"❌ No se puede obtener o generar 'Close' para {ticker}")
                    return None

            if "datetime" not in df.columns:
                logger.error(f"❌ Columna 'datetime' faltante para {ticker}")
                return None

            df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")
            df.set_index("datetime", inplace=True)
            df.sort_index(inplace=True)

            for col in ['open', 'high', 'low', 'Close', 'volume']:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')

            df.dropna(subset=['Close'], inplace=True)

            if df.empty:
                logger.warning(f"⚠️ DataFrame vacío después de limpieza para {ticker}")
                return None

            logger.info(f"✅ Datos obtenidos para {ticker} ({len(df)} registros)")
            return df

        except Exception as e:
            logger.error(f"❌ Excepción al obtener datos de {ticker}: {e}")

        if intento < max_intentos:
            logger.warning(f"🔄 Reintentando {ticker} en 5 segundos...")
            time.sleep(5)

    logger.error(f"❌ Fallo definitivo para {ticker}: 'Close'")
    return None
