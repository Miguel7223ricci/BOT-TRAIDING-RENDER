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

  # Acciones estadounidenses
        "Apple Inc": "AAPL",
        "Tesla Inc": "TSLA",
        "CoroWare Inc": "COWI",
        "Microsoft Corp.": "MSFT",
        "Alphabet Inc.": "GOOG",
        "Amazon.com Inc.": "AMZN",
        "Meta Platforms Inc.": "META",
        "Intel Corp.": "INTC",

        # ETFs estadounidenses
        "SPDR S&P 500 ETF Trust": "SPY",
        "Direxion Semiconductor Bear 3X": "SOXS",
        "UltraPro Short QQQ": "SQQQ",
        "GraniteShares COIN 1.5x ETF": "CONL",
        "Invesco QQQ Trust": "QQQ",
        "iShares Russell 2000": "IWM",
        "iShares Emerging Markets": "EEM",
        "SPDR Dow Jones Industrial": "DIA",
    },
    "intervalo": "1h",
    "periodo": "60d",
    "modelo_path": "modelo_trained_rf_pro.pkl",
    "umbral_confianza": 0.55,
    "pausa_horas": 2
}

