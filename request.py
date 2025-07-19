import os
import requests
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

API_KEY = os.getenv("APCA_API_KEY_ID")
API_SECRET = os.getenv("APCA_API_SECRET_KEY")
BASE_URL = "https://data.alpaca.markets/v1beta1/forex"

HEADERS = {
    "APCA-API-KEY-ID": API_KEY,
    "APCA-API-SECRET-KEY": API_SECRET
}

def obtener_datos_forex(par="EUR/USD", start="2024-07-01", end="2024-07-18", timeframe="1Hour"):
    url = f"{BASE_URL}/bars"
    params = {
        "symbols": par.replace("/", ""),  # EURUSD
        "timeframe": timeframe,
        "start": start,
        "end": end,
        "limit": 1000
    }

    response = requests.get(url, headers=HEADERS, params=params)
    
    if response.status_code != 200:
        print(f"❌ Error: {response.status_code} - {response.text}")
        return None

    data = response.json()
    if par.replace("/", "") not in data:
        print("❌ Par no encontrado en los datos.")
        return None
    
    df = pd.DataFrame(data[par.replace("/", "")])
    df['t'] = pd.to_datetime(df['t'])
    return df

# Ejemplo
df = obtener_datos_forex("EUR/USD")
if df is not None:
    print(df.head())
