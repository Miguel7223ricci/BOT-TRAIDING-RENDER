from datetime import datetime
import pandas as pd
import numpy as np

def evaluar_estrategia(nombre, df, modelo, umbral_confianza):
    if df is None or len(df) < 50:
        return []

    df = df.copy()
    ultima = df.iloc[-1]

    # Usar nombres de columnas en minúsculas
    precio = ultima['close']
    atr = ultima['atr']
    ema_rapida = ultima['ema_rapida']
    ema_lenta = ultima['ema_lenta']
    rsi = ultima['rsi']

    # Validar DataFrames de sesiones
    rompimientos = []
    df['hora'] = df.index.hour
    
    # Asiático (00:00-06:00 UTC)
    asiatico = df.between_time('00:00', '06:00')
    if not asiatico.empty and (precio > asiatico['high'].max() or precio < asiatico['low'].min()):
        rompimientos.append("Asiático")
    
    # Londres (06:00-12:00 UTC)
    londres = df.between_time('06:00', '12:00')
    if not londres.empty and (precio > londres['high'].max() or precio < londres['low'].min()):
        rompimientos.append("Londres")
    
    # NYSE (13:00-20:00 UTC)
    nyse = df.between_time('13:00', '20:00')
    if not nyse.empty and (precio > nyse['high'].max() or precio < nyse['low'].min()):
        rompimientos.append("EE.UU.")

    if not rompimientos:
        return []

    # Predicción ML (sin 'Direccion_Num')
    confianza = 0.0
    if modelo:
        entrada_ml = pd.DataFrame([{
            "ATR": atr,
            "EMA_Rapida": ema_rapida,
            "EMA_Lenta": ema_lenta,
            "RSI": rsi
        }])
        
        try:
            proba = modelo.predict_proba(entrada_ml)[0]
            if "GANANCIA" in modelo.classes_:
                clase_idx = list(modelo.classes_).index("GANANCIA")
                confianza = proba[clase_idx]
            else:
                confianza = np.max(proba)
        except Exception as e:
            print(f"Error en ML: {str(e)}")
            confianza = 0.0

    if confianza < umbral_confianza:
        return []

    # Generar señales con SL/TP basado en ATR
    señales = []
    
    # Señal COMPRA
    if ema_rapida > ema_lenta and 40 < rsi < 70:
        sl = precio - atr * 1.5
        tp = precio + atr * 2
        mensaje = formatear_mensaje(
            nombre, "BUY", precio, sl, tp,
            atr, ema_rapida, ema_lenta, rsi, confianza, rompimientos
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
    
    # Señal VENTA
    if ema_rapida < ema_lenta and 30 < rsi < 60:
        sl = precio + atr * 1.5
        tp = precio - atr * 2
        mensaje = formatear_mensaje(
            nombre, "SELL", precio, sl, tp,
            atr, ema_rapida, ema_lenta, rsi, confianza, rompimientos
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
    
    return señales

def formatear_mensaje(activo, direccion, precio, stop, target,
                      atr, ema_r, ema_l, rsi, confianza, rangos):
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
