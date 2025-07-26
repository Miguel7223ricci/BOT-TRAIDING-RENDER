# swing_detection.py
import numpy as np
import pandas as pd

def detectar_swings(high, low, window=5):
    """
    Detecta swings highs y lows usando un enfoque de máximos/mínimos locales.
    
    Args:
        high (pd.Series): Serie de precios máximos
        low (pd.Series): Serie de precios mínimos
        window (int): Tamaño de la ventana para detección de swings
    
    Returns:
        tuple: (swing_highs, swing_lows) como Series de pandas
    """
    swing_highs = high.copy()
    swing_lows = low.copy()
    
    # Identificar máximos locales
    for i in range(window, len(high)-window):
        if high.iloc[i] == high.iloc[i-window:i+window+1].max():
            swing_highs.iloc[i] = high.iloc[i]
        else:
            swing_highs.iloc[i] = np.nan
    
    # Identificar mínimos locales
    for i in range(window, len(low)-window):
        if low.iloc[i] == low.iloc[i-window:i+window+1].min():
            swing_lows.iloc[i] = low.iloc[i]
        else:
            swing_lows.iloc[i] = np.nan
    
    # Forward fill para llevar el último swing válido
    swing_highs = swing_highs.ffill()
    swing_lows = swing_lows.ffill()
    
    return swing_highs, swing_lows
