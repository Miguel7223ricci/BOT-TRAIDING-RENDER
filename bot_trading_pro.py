# bot_trading_pro.py

import os
import time
import joblib
import logging
from datetime import datetime
from dotenv import load_dotenv
from data_providers import obtener_datos
from indicadores_tecnicos import calcular_indicadores
from estrategia_trading import evaluar_estrategia
from whatsapp_sender import enviar_whatsapp
from config_activos import CONFIG
import pandas as pd

load_dotenv()

RESULTADOS_PATH = "resultados_estrategia.csv"

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# ======= Cargar modelo ML ===========
try:
    modelo = joblib.load(CONFIG["modelo_path"])
    logger.info("✅ Modelo ML cargado exitosamente")
except Exception as e:
    logger.error(f"❌ Error cargando el modelo ML: {e}")
    modelo = None

# ======= Evaluar activo individual ===========
def evaluar_activo(nombre, ticker):
    logger.info(f"🔍 Evaluando {nombre} ({ticker})")
    df = obtener_datos(ticker, CONFIG["intervalo"], CONFIG["periodo"])

    if df is None:
        logger.warning(f"⚠️ No se pudo obtener datos para {nombre}")
        return

    if "CLOSE" not in df.columns:
        logger.error(f"❌ Columna 'close' faltante en datos para {nombre}")
        return

    if len(df) < 80:
        logger.warning(f"⚠️ No hay suficientes datos ({len(df)} filas) para {nombre}")
        return

    df = calcular_indicadores(df)

    if modelo is None:
        logger.error("❌ Modelo ML no cargado, omitiendo evaluación")
        return

    señales = evaluar_estrategia(nombre, df, modelo, CONFIG["umbral_confianza"])
    for señal in señales:
        enviar_whatsapp(señal)
        registrar_senal(señal["activo"], señal["fecha"], señal["precio"], señal["tipo"], CONFIG["modelo_path"])

# ======= Registrar señales ===========
def registrar_senal(activo, fecha, precio_actual, senal, modelo_path):
    try:
        with open(RESULTADOS_PATH, "a") as f:
            f.write(f"{activo},{fecha},{precio_actual},{senal},{modelo_path}\n")
    except Exception as e:
        logger.error(f"❌ Error al registrar señal: {e}")

# ======= Loop principal ===========
def monitorear():
    while True:
        logger.info("\n🚀 Iniciando nuevo ciclo de monitoreo")

        for nombre, ticker in CONFIG["activos"].items():
            try:
                evaluar_activo(nombre, ticker)
                time.sleep(8)  # Control de 8 requests/minuto para plan free
            except Exception as e:
                if "API credits" in str(e):
                    logger.info("⏳ Límite de créditos alcanzado, esperando 60 segundos...")
                    time.sleep(60)
                logger.error(f"❌ Error evaluando {nombre}: {e}")

        logger.info(f"⏸️ Ciclo finalizado. Esperando {CONFIG['pausa_horas']}h...")
        time.sleep(CONFIG["pausa_horas"] * 3600)

if __name__ == "__main__":
    monitorear()

