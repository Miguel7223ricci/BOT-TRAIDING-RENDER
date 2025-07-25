from datetime import datetime
import pandas as pd
import logging
from indicadores_tecnicos import calcular_indicadores

logger = logging.getLogger(__name__)

def evaluar_estrategia(activo, df, modelo=None, umbral_confianza=0.6):
    if df is None or len(df) < 60:
        logger.warning(f"⚠️ {activo} tiene datos insuficientes ({len(df)} filas)")
        return []

    df = calcular_indicadores(df.copy())

    required_cols = ['close', 'atr', 'ema_35', 'ema_50', 'rsi', 'adx', 'swing_high', 'swing_low']
    if not all(col in df.columns for col in required_cols):
        logger.error(f"❌ Faltan columnas requeridas en {activo}: {df.columns.tolist()}")
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

    if not adx_ok:
        logger.info(f"⛔ ADX insuficiente en {activo} ({adx:.2f})")
        return []

    señales = []


    logger.info(f"🔎 Indicadores {activo}:")
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

    if rebote_long and rsi_long_ok:
        sl = fibo_618 - buffer
        tp = precio + 2 * (precio - sl)
        mensaje = formatear_mensaje(
            activo, "BUY", precio, sl, tp,
            atr, ema_35, ema_50, rsi, adx, "EMA+Fibo+RSI+ADX"
        )
        señales.append({
            "activo": activo,
            "tipo": "BUY",
            "precio": precio,
            "sl": sl,
            "tp": tp,
            "mensaje": mensaje,
            "fecha": datetime.now()
        })

    if rebote_short and rsi_short_ok:
        sl = fibo_618 + buffer
        tp = precio - 2 * (sl - precio)
        mensaje = formatear_mensaje(
            activo, "SELL", precio, sl, tp,
            atr, ema_35, ema_50, rsi, adx, "EMA+Fibo+RSI+ADX"
        )
        señales.append({
            "activo": activo,
            "tipo": "SELL",
            "precio": precio,
            "sl": sl,
            "tp": tp,
            "mensaje": mensaje,
            "fecha": datetime.now()
        })

    if señales:
        logger.info(f"✅ Señales generadas para {activo}: {[s['tipo'] for s in señales]}")
    else:
        logger.info(f"ℹ️ No se generaron señales para {activo}")

    return señales

def formatear_mensaje(activo, tipo, precio, sl, tp, atr, ema_r, ema_l, rsi, adx, criterio):
    return f"""
🔔 *SEÑAL DE TRADING ({tipo})* - {datetime.now().strftime('%Y-%m-%d %H:%M')}
• Activo: {activo}
• Precio: {precio:.5f}
• Stop Loss: {sl:.5f}
• Take Profit: {tp:.5f}
• ATR: {atr:.5f}
• EMA 35: {ema_r:.5f}
• EMA 50: {ema_l:.5f}
• RSI: {rsi:.2f}
• ADX: {adx:.2f}
• Criterio: {criterio}
"""