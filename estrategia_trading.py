

import pandas as pd
import numpy as np
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def evaluar_estrategia(nombre, df, modelo, umbral_confianza):
    if df is None or len(df) < 60:
        return []

    df = df.copy()
    # 🔄 Calcular swing_high y swing_low antes de definir 'ultima'
    if 'swing_high' not in df.columns or df['swing_high'].isna().all():
        df['swing_high'] = df['high'].rolling(window=20).max()
    if 'swing_low' not in df.columns or df['swing_low'].isna().all():
        df['swing_low'] = df['low'].rolling(window=20).min()

    logger.debug(f"🧪 Últimos valores high: {df['high'].tail(5).tolist()}")
    logger.debug(f"🧪 Últimos valores low: {df['low'].tail(5).tolist()}")
    logger.debug(f"🧪 Últimos valores swing_high: {df['swing_high'].tail(5).tolist()}")
    logger.debug(f"🧪 Últimos valores swing_low: {df['swing_low'].tail(5).tolist()}")


    # Calcular swing_high y swing_low si no existen
    if 'swing_high' not in df.columns or df['swing_high'].isna().all():
        df['swing_high'] = df['high'].rolling(window=20).max()
    if 'swing_low' not in df.columns or df['swing_low'].isna().all():
        df['swing_low'] = df['low'].rolling(window=20).min()


    required_cols = ['close', 'atr', 'ema_35', 'ema_50', 'rsi', 'adx', 'swing_high', 'swing_low']
    if not all(col in df.columns for col in required_cols):
        logger.error(f"❌ Faltan columnas en {nombre}. Disponibles: {df.columns.tolist()}")
        return []

    ultima = df.iloc[-1]
    precio = ultima['close']
    atr = ultima['atr']
    ema_35 = ultima['ema_35']
    ema_50 = ultima['ema_50']
    rsi = ultima['rsi']
    adx = ultima['adx']
    swing_high = ultima['swing_high']
    swing_low = ultima['swing_low']

    tendencia_alcista = ema_35 > ema_50
    tendencia_bajista = ema_35 < ema_50

    fibo_start = swing_low if tendencia_alcista else swing_high
    fibo_end = swing_high if tendencia_alcista else swing_low

    fibo_500 = fibo_start + 0.5 * (fibo_end - fibo_start)
    fibo_618 = fibo_start + 0.618 * (fibo_end - fibo_start)
    buffer = 0.0005

    rebote_long = tendencia_alcista and (ultima['low'] <= fibo_618 and ultima['close'] >= fibo_500)
    rebote_short = tendencia_bajista and (ultima['high'] >= fibo_618 and ultima['close'] <= fibo_500)

    rsi_long_ok = rsi > 45 and rsi < 60 and df['rsi'].diff().iloc[-1] > 0
    rsi_short_ok = rsi < 55 and rsi > 40 and df['rsi'].diff().iloc[-1] < 0
    adx_ok = adx > 20

    logger.info(f"🔎 Indicadores {nombre}:")
    logger.info(f"   • Precio: {precio:.5f}")
    logger.info(f"   • EMA 35: {ema_35:.5f} | EMA 50: {ema_50:.5f}")
    logger.info(f"   • RSI: {rsi:.2f}")
    logger.info(f"   • ADX: {adx:.2f}")
    logger.info(f"   • Swing High: {swing_high:.5f} | Swing Low: {swing_low:.5f}")
    logger.info(f"   • Fibo 0.618: {fibo_618:.5f} | Fibo 0.5: {fibo_500:.5f}")
    logger.info(f"   • Último LOW: {ultima['low']:.5f} | HIGH: {ultima['high']:.5f} | CLOSE: {ultima['close']:.5f}")

    if not adx_ok:
        logger.info(f"⛔ ADX demasiado bajo: {adx:.2f} (debe ser > 20)")

    if tendencia_alcista:
        if not rebote_long:
            logger.info("⛔ No hay rebote LONG válido (Fibo + EMA)")
        if not rsi_long_ok:
            logger.info(f"⛔ RSI no confirma LONG: {rsi:.2f} (debe estar entre 45-60 y en subida)")
    elif tendencia_bajista:
        if not rebote_short:
            logger.info("⛔ No hay rebote SHORT válido (Fibo + EMA)")
        if not rsi_short_ok:
            logger.info(f"⛔ RSI no confirma SHORT: {rsi:.2f} (debe estar entre 40-55 y en bajada)")
    else:
        logger.info("⛔ No hay tendencia clara (EMA35 ≈ EMA50)")


    señales = []

    if rebote_long and rsi_long_ok and adx_ok:
        sl = fibo_618 - buffer
        tp = precio + 2 * (precio - sl)
        mensaje = formatear_mensaje(
            nombre, "BUY", precio, sl, tp,
            atr, ema_35, ema_50, rsi, adx, "EMA+Fibo+RSI+ADX"
        )
        señales.append({
            "activo": nombre,
            "tipo": "BUY",
            "precio": precio,
            "sl": sl,
            "tp": tp,
            "mensaje": mensaje,
            "fecha": datetime.now()
        })

    if rebote_short and rsi_short_ok and adx_ok:
        sl = fibo_618 + buffer
        tp = precio - 2 * (sl - precio)
        mensaje = formatear_mensaje(
            nombre, "SELL", precio, sl, tp,
            atr, ema_35, ema_50, rsi, adx, "EMA+Fibo+RSI+ADX"
        )
        señales.append({
            "activo": nombre,
            "tipo": "SELL",
            "precio": precio,
            "sl": sl,
            "tp": tp,
            "mensaje": mensaje,
            "fecha": datetime.now()
        })

    if señales:
        logger.info(f"✅ Señales generadas para {nombre}: {[s['tipo'] for s in señales]}")
    else:
        logger.info(f"ℹ️ No se generaron señales para {nombre}")

    return señales

def formatear_mensaje(activo, direccion, precio, stop, target,
                      atr, ema_r, ema_l, rsi, adx, criterio):
    return f"""
🔔 *SEÑAL DE TRADING ({direccion})* - {datetime.now().strftime('%Y-%m-%d %H:%M')}
• Activo: {activo}
• Precio: {precio:.5f}
• Stop Loss: {stop:.5f}
• Take Profit: {target:.5f}
• ATR: {atr:.5f}
• EMA 35: {ema_r:.5f}
• EMA 50: {ema_l:.5f}
• RSI: {rsi:.2f}
• ADX: {adx:.2f}
• Criterio: {criterio}
"""