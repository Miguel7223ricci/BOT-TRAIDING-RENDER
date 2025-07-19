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

def obtener_datos(ticker, intervalo="4h", periodo="60d"):
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
        "apikey": API_KEY,
        "outputsize": 5000
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()

        # Manejar errores de API
        if "status" in data and data["status"] == "error":
            error_msg = data.get('message', 'Error desconocido')
            logger.error(f"❌ Error API para {ticker}: {error_msg}")
            
            # Manejo específico de límites de crédito
            if "run out of API credits" in error_msg:
                logger.info("⏳ Límite de créditos alcanzado, esperando 60 segundos...")
                time.sleep(60)
            return None

        # Manejar estructura de datos variable
        if "values" in data:
            valores = data["values"]
        elif "data" in data:
            valores = data["data"]
        else:
            logger.error(f"❌ Estructura de datos desconocida para {ticker}")
            return None

        if not valores:
            logger.warning(f"⚠️ Sin datos para {ticker}")
            return None

        df = pd.DataFrame(valores)
        
        # Normalización robusta de nombres de columna
        df.columns = [col.lower() for col in df.columns]
        column_mapping = {
            'close': 'close',
            'closing': 'close',
            'price': 'close',
            'value': 'close',
            'datetime': 'datetime',
            'date': 'datetime',
            'time': 'datetime'
        }
        
        # Renombrar columnas existentes
        df.rename(columns={k: v for k, v in column_mapping.items() 
                          if k in df.columns}, inplace=True)
        
        logger.info(f"📊 Columnas recibidas para {ticker}: {df.columns.tolist()}")

        # Verificar columna 'close'
        if "close" not in df.columns:
            # Intentar derivar 'close' si hay columnas OHLC
            if all(col in df.columns for col in ['open', 'high', 'low']):
                logger.warning(f"⚠️ Generando 'close' como promedio OHLC para {ticker}")
                df['close'] = (df['open'] + df['high'] + df['low']) / 3
            else:
                logger.error(f"❌ No se puede obtener o generar 'close' para {ticker}")
                return None

        # Procesamiento de fechas
        if "datetime" not in df.columns:
            logger.error(f"❌ Columna 'datetime' faltante para {ticker}")
            return None
            
        df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")
        df.set_index("datetime", inplace=True)
        df = df.sort_index()  # Ordenar cronológicamente

        # Convertir columnas numéricas
        numeric_cols = ['open', 'high', 'low', 'close', 'volume']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        # Eliminar filas con valores faltantes en 'close'
        df.dropna(subset=['close'], inplace=True)
        
        if df.empty:
            logger.warning(f"⚠️ DataFrame vacío después de limpieza para {ticker}")
            return None

        logger.info(f"✅ Datos obtenidos para {ticker} ({len(df)} registros)")
        return df

    except Exception as e:
        logger.exception(f"❌ Excepción crítica al obtener datos de {ticker}: {e}")
        return None