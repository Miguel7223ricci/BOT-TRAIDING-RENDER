# bot_trading_pro.py

import os
import time
import joblib
import logging
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from data_providers import obtener_datos
from indicadores_tecnicos import calcular_indicadores
from estrategia_trading import evaluar_estrategia
from whatsapp_sender import enviar_whatsapp

# ========================== CONFIGURACIÓN ===============================

load_dotenv()

CONFIG = {
    "activos": {
        "EURUSD": "EURUSD=X", "EURNZD": "EURNZD=X", "GBPNZD": "GBPNZD=X",
        "GBPJPY": "GBPJPY=X", "USDNOK": "USDNOK=X", "USDCHF": "USDCHF=X",
        "USDSEK": "USDSEK=X", "EURSEK": "EURSEK=X", "GBPAUD": "GBPAUD=X",
        "AUDNZD": "AUDNZD=X", "NZDUSD": "NZDUSD=X", "EURCAD": "EURCAD=X",
        "AUDUSD": "AUDUSD=X", "EURAUD": "EURAUD=X", "CADJPY": "CADJPY=X",
        "NATGAS": "NG=F", "GOLD": "GC=F", "WTI": "CL=F", "PALLADIUM": "PA=F",
        "SOLANA": "SOL-USD", "BTC": "BTC-USD", "ETH": "ETH-USD",
        "US2000": "^RUT", "US500": "^GSPC", "US30": "^DJI", "EU50": "^STOXX50E",
        "AAPL": "AAPL", "MSFT": "MSFT", "TSLA": "TSLA", "AMZN": "AMZN", "META": "META", "NVDA": "NVDA"
    },
    "intervalo": "4h",
    "periodo": "60d",
    "modelo_path": "modelo_trained_rf_pro.pkl",
    "umbral_confianza": 0.55,
    "pausa_horas": 4
}

# ========================== LOGGING ===============================

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# ========================== CARGA MODELO ===============================

try:
    modelo = joblib.load(CONFIG["modelo_path"])
    logger.info("✅ Modelo ML cargado exitosamente")
except Exception as e:
    logger.error(f"❌ Error cargando el modelo ML: {e}")
    modelo = None

# ========================== EVALUAR ACTIVO ===============================

def evaluar_activo(nombre, ticker):
    logger.info(f"🔍 Evaluando {nombre} ({ticker})")
    df = obtener_datos(ticker, CONFIG["intervalo"], CONFIG["periodo"])
    if df is None or len(df) < 80:
        logger.warning(f"⚠️ No hay suficientes datos para {nombre}")
        return

    df = calcular_indicadores(df)
    señales = evaluar_estrategia(nombre, df, modelo, CONFIG["umbral_confianza"])
    for señal in señales:
        enviar_whatsapp(señal)

# ========================== LOOP PRINCIPAL ===============================

def monitorear():
    while True:
        logger.info("\n🚀 Iniciando nuevo ciclo de monitoreo")
        for nombre, ticker in CONFIG["activos"].items():
            try:
                evaluar_activo(nombre, ticker)
            except Exception as e:
                logger.error(f"❌ Error evaluando {nombre}: {e}")
        logger.info(f"⏸️ Ciclo finalizado. Esperando {CONFIG['pausa_horas']}h...")
        time.sleep(CONFIG['pausa_horas'] * 60 * 60)

if __name__ == "__main__":
    monitorear()

import os
from datetime import datetime

RESULTADOS_PATH = "resultados_estrategia.csv"
VENTANA_RETARDO_VIVO = 4  # intervalos de 4h

def registrar_senal(activo, fecha, precio_actual, senal, modelo_path):
    with open(RESULTADOS_PATH, "a") as f:
        f.write(f"{activo},{fecha},{precio_actual},{senal},{modelo_path},,\n")
