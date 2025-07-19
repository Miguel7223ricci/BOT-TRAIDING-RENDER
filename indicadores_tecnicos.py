import pandas as pd

def calcular_indicadores(df: pd.DataFrame) -> pd.DataFrame:
    # Normalizar nombres de columnas a mayúsculas
    df.columns = [col.upper() for col in df.columns]

    # Calcular indicadores simples
    df['H-L'] = df['HIGH'] - df['LOW']
    df['O-C'] = df['OPEN'] - df['CLOSE']
    df['MA10'] = df['CLOSE'].rolling(window=10).mean()
    df['MA50'] = df['CLOSE'].rolling(window=50).mean()
    df['STDDEV'] = df['CLOSE'].rolling(window=10).std()
    
    # Eliminar NaN iniciales por rolling
    df.dropna(inplace=True)

    return df
