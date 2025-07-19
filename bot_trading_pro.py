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
def evaluar_activo(nombre, ticker, intento=1):
    max_intentos = 3
    try:
        logger.info(f"🔍 Evaluando {nombre} ({ticker}) [Intento {intento}]")
        df = obtener_datos(ticker, CONFIG["intervalo"], CONFIG["periodo"])

        if df is None:
            logger.warning(f"⚠️ No se pudo obtener datos para {nombre}")
            return []

        if "close" not in df.columns:
            logger.error(f"❌ Columna 'close' faltante en datos para {nombre}")
            return []

        if len(df) < 80:
            logger.warning(f"⚠️ No hay suficientes datos ({len(df)} filas) para {nombre}")
            return []

        df = calcular_indicadores(df)

        if modelo is None:
            logger.error("❌ Modelo ML no cargado, omitiendo evaluación")
            return []

        señales = evaluar_estrategia(nombre, df, modelo, CONFIG["umbral_confianza"])

        for señal in señales:
            enviar_whatsapp(señal["mensaje"])
            registrar_senal(
                señal["activo"],
                datetime.now(),
                señal["precio"],
                señal["tipo"],
                CONFIG["modelo_path"]
            )

        return señales

    except Exception as e:
        if intento < max_intentos:
            logger.warning(f"🔄 Reintentando {nombre} en 5 segundos...")
            time.sleep(5)
            return evaluar_activo(nombre, ticker, intento + 1)
        else:
            logger.error(f"❌ Fallo definitivo para {nombre}: {str(e)}")
            return []

# ======= Registrar señales ===========
def registrar_senal(activo, fecha, precio_actual, senal, modelo_path):
    try:
        with open(RESULTADOS_PATH, "a") as f:
            f.write(f"{activo},{fecha},{precio_actual},{senal},{modelo_path}\n")
    except Exception as e:
        logger.error(f"❌ Error al registrar señal: {e}")

# ======= Sistema de límite de API ===========
class APIRateLimiter:
    def __init__(self, max_requests=8, period=60):
        self.max_requests = max_requests
        self.period = period
        self.request_count = 0
        self.last_reset = time.time()

    def check_limit(self):
        current_time = time.time()
        if current_time - self.last_reset > self.period:
            self.request_count = 0
            self.last_reset = current_time

        if self.request_count >= self.max_requests:
            sleep_time = self.period - (current_time - self.last_reset) + 1
            logger.warning(f"⏳ Límite API alcanzado. Esperando {sleep_time:.1f}s...")
            time.sleep(sleep_time)
            self.request_count = 0
            self.last_reset = time.time()

# ======= Loop principal ===========
def monitorear():
    rate_limiter = APIRateLimiter(max_requests=8, period=60)

    while True:
        logger.info("\n🚀 Iniciando nuevo ciclo de monitoreo")
        activos_sin_senal = []

        for nombre, ticker in CONFIG["activos"].items():
            try:
                rate_limiter.check_limit()
                señales = evaluar_activo(nombre, ticker)
                rate_limiter.request_count += 1
                time.sleep(1)

                if not señales:
                    activos_sin_senal.append(nombre)

            except Exception as e:
                logger.error(f"❌ Error en ciclo principal para {nombre}: {str(e)}")

        # Enviar resumen de activos sin señal
        if activos_sin_senal:
            mensaje_resumen = (
                f"📋 *Resumen del monitoreo ({datetime.now().strftime('%Y-%m-%d %H:%M')})*\n"
                "No se encontraron señales en los siguientes activos:\n"
                + "\n".join(f"• {activo}" for activo in activos_sin_senal)
            )
            enviar_whatsapp(mensaje_resumen)

        logger.info(f"⏸️ Ciclo finalizado. Esperando {CONFIG['pausa_horas']}h...")
        time.sleep(CONFIG["pausa_horas"] * 3600)

if __name__ == "__main__":
    monitorear()

