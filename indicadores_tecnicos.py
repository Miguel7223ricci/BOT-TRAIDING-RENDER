import pandas as pd

def calcular_ema(series, periodo):
    return series.ewm(span=periodo, adjust=False).mean()

def calcular_rsi(series, periodo):
    delta = series.diff()
    ganancia = delta.where(delta > 0, 0)
    perdida = -delta.where(delta < 0, 0)
    
    # Usar promedio móvil suavizado
    avg_ganancia = ganancia.ewm(alpha=1/periodo, adjust=False).mean()
    avg_perdida = perdida.ewm(alpha=1/periodo, adjust=False).mean()
    
    rs = avg_ganancia / avg_perdida
    return 100 - (100 / (1 + rs))

def calcular_atr(df, periodo):
    high = df['high']
    low = df['low']
    close = df['close']
    
    hl = high - low
    hc = abs(high - close.shift())
    lc = abs(low - close.shift())
    
    tr = pd.concat([hl, hc, lc], axis=1).max(axis=1)
    return tr.ewm(span=periodo, adjust=False).mean()

def calcular_indicadores(df):
    # Asegurar minúsculas
    df.columns = [col.lower() for col in df.columns]
    
    # Calcular indicadores
    df['ema_rapida'] = calcular_ema(df['close'], 25)
    df['ema_lenta'] = calcular_ema(df['close'], 50)
    df['rsi'] = calcular_rsi(df['close'], 14)
    df['atr'] = calcular_atr(df, 14)
    
    return df
