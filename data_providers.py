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

        # Normalizar nombres de columnas con capitalización (no todo mayúsculas)
        df.columns = [col.capitalize() for col in df.columns]
        logger.debug(f"📊 Columnas disponibles para {ticker}: {df.columns.tolist()}")

        if "Close" not in df.columns or "Datetime" not in df.columns:
            logger.error(f"❌ Faltan columnas esenciales ('Close' o 'Datetime') en datos de {ticker}")
            return None

        df["Datetime"] = pd.to_datetime(df["Datetime"], errors="coerce")
        df.set_index("Datetime", inplace=True)

        # Convertir columnas numéricas
        for col in ["Open", "High", "Low", "Close", "Volume"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        df.dropna(inplace=True)
        df = df.sort_index()

        return df

    except Exception as e:
        logger.exception(f"❌ Excepción al obtener datos de {ticker}: {e}")
        return None
