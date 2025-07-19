# estrategia_trading.py

from datetime import datetime
import pandas as pd

def evaluar_estrategia(nombre, df, modelo, umbral_confianza):
    """Evalúa señales de trading (compra y venta) para un activo."""
    señales = []

    df = df.copy()
    ultima = df.iloc[-1]

    # Extraer datos técnicos
    precio = ultima['close']
    atr = ultima['ATR']
    ema_rapida = ultima['EMA_Rapida']
    ema_lenta = ultima['EMA_Lenta']
    rsi = ultima['RSI']
    soporte = ultima['Soporte']
    resistencia = ultima['Resistencia']

    # Rangos de sesión (hora UTC)
    df['hora'] = df.index.hour
    asiatico = df.between_time('00:00', '06:00')
    londres = df.between_time('06:00', '12:00')
    nyse = df.between_time('13:00', '20:00')

    rango_asiatico = (asiatico['High'].max(), asiatico['Low'].min())
    rango_londres = (londres['High'].max(), londres['Low'].min())
    rango_nyse = (nyse['High'].max(), nyse['Low'].min())

    rompimientos = []
    if precio > rango_asiatico[0] or precio < rango_asiatico[1]:
        rompimientos.append("Asiático")
    if precio > rango_londres[0] or precio < rango_londres[1]:
        rompimientos.append("Londres")
    if precio > rango_nyse[0] or precio < rango_nyse[1]:
        rompimientos.append("EE.UU.")

    if not rompimientos:
        return []

    # Predicción del modelo ML
    if modelo:
        entrada_ml = pd.DataFrame([{
            "ATR": atr,
            "EMA_Rapida": ema_rapida,
            "EMA_Lenta": ema_lenta,
            "RSI": rsi,
            "Direccion_Num": 1
        }])
        proba = modelo.predict_proba(entrada_ml)[0]
        clase_idx = list(modelo.classes_).index("GANANCIA")
        confianza = proba[clase_idx]
    else:
        confianza = 0.0

    if confianza < umbral_confianza:
        return []

    # Señales de COMPRA (BUY)
    if ema_rapida > ema_lenta and rsi > 40 and rsi < 70:
        mensaje = formatear_mensaje(
            nombre, "BUY", precio, soporte, resistencia,
            atr, ema_rapida, ema_lenta, rsi, confianza, rompimientos
        )
        señales.append(mensaje)

    # Señales de VENTA (SELL)
    if ema_rapida < ema_lenta and rsi < 60 and rsi > 30:
        mensaje = formatear_mensaje(
            nombre, "SELL", precio, resistencia, soporte,
            atr, ema_rapida, ema_lenta, rsi, confianza, rompimientos
        )
        señales.append(mensaje)

    return señales

def formatear_mensaje(activo, direccion, precio, stop, target,
                      atr, ema_r, ema_l, rsi, confianza, rangos):
    """Genera el mensaje WhatsApp con todos los datos clave."""
    return f"""
🔔 *SEÑAL DE TRADING ({direccion})* - {datetime.now().strftime('%Y-%m-%d %H:%M')}
• Activo: {activo}
• Precio: {precio:.5f}
• Stop Loss: {stop:.5f}
• Take Profit: {target:.5f}
• ATR: {atr:.5f}
• EMA Rápida: {ema_r:.5f}
• EMA Lenta: {ema_l:.5f}
• RSI: {rsi:.2f}
• Confianza ML: {confianza:.2%}
• Rango roto: {', '.join(rangos)}
"""
