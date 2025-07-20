# evaluar_estrategia.py

from datetime import datetime
import pandas as pd
from indicadores_tecnicos import calcular_indicadores

def evaluar_estrategia(activo, df, modelo=None, umbral_confianza=0.6):
    if df is None or len(df) < 50:
        return []

    df = calcular_indicadores(df.copy())
    df["hora"] = df.index.hour

    ultima = df.iloc[-1]
    # CORRECCIÓN: Usar nombres en minúsculas
    atr = ultima["atr"]
    ema_rapida = ultima["ema_rapida"]
    ema_lenta = ultima["ema_lenta"]
    rsi = ultima["rsi"]
    precio = ultima["close"]

    # Análisis de sesiones horarias
    asiatico = df.between_time("00:00", "06:00")
    londres = df.between_time("06:00", "12:00")
    nyse = df.between_time("13:00", "20:00")

    rompimientos = []
    if precio > asiatico["high"].max() or precio < asiatico["low"].min():
        rompimientos.append("Asiático")
    if precio > londres["high"].max() or precio < londres["low"].min():
        rompimientos.append("Londres")
    if precio > nyse["high"].max() or precio < nyse["low"].min():
        rompimientos.append("EE.UU.")

    if not rompimientos:
        return []

    señales = []

    # -------- PREDICCIÓN CON MODELO ML --------
    if modelo:
        # CORRECCIÓN: Usar nombres en minúsculas consistentes
        entrada_ml = pd.DataFrame([{
            "atr": atr,
            "ema_rapida": ema_rapida,
            "ema_lenta": ema_lenta,
            "rsi": rsi
        }])
      
        try:
            proba = modelo.predict_proba(entrada_ml)[0]
            clase_idx = proba.argmax()
            clase = modelo.classes_[clase_idx]
            confianza = proba[clase_idx]
        except Exception as e:
            print(f"[ERROR] ❌ Error en predicción ML para {activo}: {e}")
            return []
    else:
        clase = "HOLD"
        confianza = 0.0

    if confianza < umbral_confianza or clase == "HOLD":
        return []

    # -------- GENERAR MENSAJE --------
    sl = precio - atr * 1.5 if clase == "BUY" else precio + atr * 1.5
    tp = precio + atr * 2 if clase == "BUY" else precio - atr * 2

    mensaje = formatear_mensaje(
        activo, clase, precio, sl, tp, atr, ema_rapida, ema_lenta, rsi, confianza, rompimientos
    )

    señales.append({
        "activo": activo,
        "tipo": clase,
        "precio": precio,
        "sl": sl,
        "tp": tp,
        "mensaje": mensaje
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
    