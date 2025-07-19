# config_activos.py

CONFIG = {
    "activos": {
        # Forex (formato: "XXX/YYY")
        "EURUSD": "EUR/USD", "EURNZD": "EUR/NZD", "GBPNZD": "GBP/NZD",
        "GBPJPY": "GBP/JPY", "USDNOK": "USD/NOK", "USDCHF": "USD/CHF",
        "USDSEK": "USD/SEK", "EURSEK": "EUR/SEK", "GBPAUD": "GBP/AUD",
        "AUDNZD": "AUD/NZD", "NZDUSD": "NZD/USD", "EURCAD": "EUR/CAD",
        "AUDUSD": "AUD/USD", "EURAUD": "EUR/AUD", "CADJPY": "CAD/JPY",

        # Criptomonedas
        "BTC": "BTC/USD", "ETH": "ETH/USD", "SOLANA": "SOL/USD",

   
    "intervalo": "4h",
    "periodo": "60d",
    "modelo_path": "modelo_trained_rf_pro.pkl",
    "umbral_confianza": 0.55,
    "pausa_horas": 4
}
