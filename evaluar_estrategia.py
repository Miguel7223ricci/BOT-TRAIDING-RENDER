# evaluar_estrategia.py

from datetime import datetime
import pandas as pd
from indicadores_tecnicos import calcular_indicadores

def evaluar_estrategia(activo, df, modelo=None, umbral_confianza=0.6):
    """
    Evalúa señales de trading para un activo utilizando análisis técnico y modelo ML (si se provee).
    Devuelve una lista de señales tipo diccionario con precio, SL, TP y mensaje.
    """
    if df is None or len(df) < 50:
        return []

    df = calcular_indicadores(df.copy())
    df["hora"] = df.index.hour

    ultima = df.iloc[-1]
    atr = ultima["ATR"]
    ema_rapida = ultima["EMA_RAPIDA"]
    ema_lenta = ultima["EMA_LENTA"]
    rsi = ultima["RSI"]
    precio = ultima["CLOSE"]

    # Opcional: análisis de sesión
    asiatico = df.between_time("00:00", "06:00")
    londres = df.between_time("06:00", "12:00")
    nyse = df.between_time("13:00", "20:00")

    rompimientos = []
    if precio > asiatico["HIGH"].max() or precio < asiatico["LOW"].min():
        rompimientos.append("Asiático")
    if precio > londres["HIGH"].max() or precio < londres["LOW"].min():
        rompimientos.append("Londres")
    if precio > nyse["HIGH"].max() or precio < nyse["LOW"].min():
        rompimientos.append("EE.UU.")

    if not rompimientos:
        return []

    señales = []

    # -------- PREDICCIÓN CON MODELO ML --------
    if modelo:
        entrada_ml = pd.DataFrame([{
            "ATR": atr,
            "EMA_Rapida": ema_rapida,
            "EMA_Lenta": ema_lenta,
            "RSI": rsi
        }])

        proba = modelo.predict_proba(entrada_ml)[0]
        clase_idx = proba.argmax()
        clase = modelo.classes_[clase_idx]
        confianza = proba[clase_idx]
    else:
        clase = "HOLD"
        confianza = 0.0

    if confianza < umbral_confianza or clase == "HOLD":
        return []

    # -------- GENERAR MENSAJE --------
    if clase == "BUY":
        sl = precio - atr * 1.5
        tp = precio + atr * 2
        mensaje = formatear_mensaje(
            activo, "BUY", precio, sl, tp, atr, ema_rapida, ema_lenta, rsi, confianza, rompimientos
        )
        señales.append({
            "activo": activo, "tipo": "BUY", "precio": precio, "sl": sl, "tp": tp, "mensaje": mensaje
        })

    elif clase == "SELL":
        sl = precio + atr * 1.5
        tp = precio - atr * 2
        mensaje = formatear_mensaje(
            activo, "SELL", precio, sl, tp, atr, ema_rapida, ema_lenta, rsi, confianza, rompimientos
        )
        señales.append({
            "activo": activo, "tipo": "SELL", "precio": precio, "sl": sl, "tp": tp, "mensaje": mensaje
        })

    return señales


def formatear_mensaje(activo, tipo, precio, sl, tp, atr, ema_r, ema_l, rsi, confianza, rangos):
    return f"""
🔔 *SEÑAL DE TRADING ({tipo})* - {datetime.now().strftime('%Y-%m-%d %H:%M')}
• Activo: {activo}
• Precio: {precio:.5f}
• Stop Loss: {sl:.5f}
• Take Profit: {tp:.5f}
• ATR: {atr:.5f}
• EMA Rápida: {ema_r:.5f}
• EMA Lenta: {ema_l:.5f}
• RSI: {rsi:.2f}
• Confianza ML: {confianza:.2%}
• Rango roto: {', '.join(rangos)}
"""
