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

# ========================== CONFIGURACIÓN ===============================

load_dotenv()

RESULTADOS_PATH = "resultados_estrategia.csv"
VENTANA_RETARDO_VIVO = 4  # Intervalos de 4h

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

    if df is None:
        logger.warning(f"⚠️ No se pudo obtener datos para {nombre}")
        return

    if not isinstance(df, pd.DataFrame) or df.empty:
        logger.warning(f"⚠️ DataFrame vacío o inválido para {nombre}")
        return

    if "Close" not in df.columns:
        logger.error(f"❌ Columna 'Close' faltante en datos para {nombre}")
        return

    if len(df) < 80:
        logger.warning(f"⚠️ No hay suficientes datos (solo {len(df)} filas) para {nombre}")
        return

    df = calcular_indicadores(df)

    if modelo is None:
        logger.error("❌ Modelo ML no está cargado, omitiendo evaluación")
        return

    señales = evaluar_estrategia(nombre, df, modelo, CONFIG["umbral_confianza"])
    for señal in señales:
        enviar_whatsapp(señal)
        registrar_senal(señal["activo"], señal["fecha"], señal["precio"], señal["tipo"], CONFIG["modelo_path"])

# ========================== REGISTRO DE SEÑALES ===============================

def registrar_senal(activo, fecha, precio_actual, senal, modelo_path):
    try:
        with open(RESULTADOS_PATH, "a") as f:
            f.write(f"{activo},{fecha},{precio_actual},{senal},{modelo_path},,\n")
    except Exception as e:
        logger.error(f"❌ Error al registrar señal: {e}")

# ========================== LOOP PRINCIPAL ===============================

def monitorear():
    while True:
        logger.info("\n🚀 Iniciando nuevo ciclo de monitoreo")

        for nombre, ticker in CONFIG["activos"].items():
            try:
                evaluar_activo(nombre, ticker)
                time.sleep(8)  # Controla uso de créditos API (máx 8 por minuto en plan free)
            except Exception as e:
                logger.error(f"❌ Error evaluando {nombre}: {e}")

        logger.info(f"⏸️ Ciclo finalizado. Esperando {CONFIG['pausa_horas']}h...")
        time.sleep(CONFIG['pausa_horas'] * 60 * 60)

if __name__ == "__main__":
    monitorear()
