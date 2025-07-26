import pandas as pd
import numpy as np
from ta.trend import EMAIndicator, ADXIndicator, SMAIndicator
from ta.momentum import RSIIndicator
from ta.volatility import AverageTrueRange
from swing_detection import detectar_swings  # Importar la nueva función


def calcular_ema(series, periodo):
    return series.ewm(span=periodo, adjust=False).mean()

def calcular_rsi(series, periodo):
    delta = series.diff()
    ganancia = delta.where(delta > 0, 0)
    perdida = -delta.where(delta < 0, 0)
    avg_ganancia = ganancia.ewm(alpha=1/periodo, adjust=False).mean()
    avg_perdida = perdida.ewm(alpha=1/periodo, adjust=False).mean()
    rs = avg_ganancia / avg_perdida
    return 100 - (100 / (1 + rs))

def calcular_adx(df, periodo):
    high = df['high']
    low = df['low']
    close = df['close']

    plus_dm = high.diff()
    minus_dm = -low.diff()
    plus_dm[plus_dm < 0] = 0
    minus_dm[minus_dm < 0] = 0

    tr1 = pd.DataFrame({
        'hl': high - low,
        'hc': abs(high - close.shift()),
        'lc': abs(low - close.shift())
    })
    tr = tr1.max(axis=1)
    atr = tr.rolling(window=periodo).mean()

    plus_di = 100 * (plus_dm.rolling(window=periodo).mean() / atr)
    minus_di = 100 * (minus_dm.rolling(window=periodo).mean() / atr)
    dx = (abs(plus_di - minus_di) / (plus_di + minus_di)) * 100
    adx = dx.rolling(window=periodo).mean()

    return adx, atr

def calcular_swing_high(series, window):
    return series.rolling(window=window, center=True).max()

def calcular_swing_low(series, window):
    return series.rolling(window=window, center=True).min()

def calcular_indicadores(df):
    df.columns = [col.lower() for col in df.columns]
    df['ema_35'] = calcular_ema(df['close'], 35)
    df['ema_50'] = calcular_ema(df['close'], 50)
    df['rsi'] = calcular_rsi(df['close'], 14)
    df['adx'], df['atr'] = calcular_adx(df, 14)
    df['swing_high'] = calcular_swing_high(df['high'], 20)
    df['swing_low'] = calcular_swing_low(df['low'], 20)
    return df
