import os
from dotenv import load_dotenv

load_dotenv()

# Quotex API Configuration
QUOTEX_EMAIL = os.getenv('QUOTEX_EMAIL', '')
QUOTEX_PASSWORD = os.getenv('QUOTEX_PASSWORD', '')

# Signal Configuration
NUMBER_OF_CANDLES = 12  # Historical candles to analyze
CANDLE_TIMEFRAME = '1m'  # 1 minute candles

# Technical Indicator Thresholds
RSI_OVERSOLD = 30
RSI_OVERBOUGHT = 70
MACD_SIGNAL_THRESHOLD = 0.0001
BB_DEVIATION = 2

# CSV Configuration
CSV_DATA_PATH = 'data/candles.csv'
CSV_COLUMNS = ['timestamp', 'open', 'high', 'low', 'close', 'volume']

# OTC Asset Pairs Configuration
OTC_ASSET_PAIRS = [
    'USD/ARS-OTC',
    'USD/COP-OTC',
    'USD/BRL-OTC',
    'USD/MXN-OTC',
    'USD/PEN-OTC',
]

# OTC Asset Data Paths (CSV files for each pair)
OTC_DATA_DIRECTORY = 'data/otc/'

# Asset Pair Configurations
ASSET_PAIR_CONFIG = {
    'USD/ARS-OTC': {
        'csv_path': f'{OTC_DATA_DIRECTORY}USD_ARS_OTC.csv',
        'timeframe': '1m',
        'description': 'US Dollar vs Argentine Peso (OTC)'
    },
    'USD/COP-OTC': {
        'csv_path': f'{OTC_DATA_DIRECTORY}USD_COP_OTC.csv',
        'timeframe': '1m',
        'description': 'US Dollar vs Colombian Peso (OTC)'
    },
    'USD/BRL-OTC': {
        'csv_path': f'{OTC_DATA_DIRECTORY}USD_BRL_OTC.csv',
        'timeframe': '1m',
        'description': 'US Dollar vs Brazilian Real (OTC)'
    },
    'USD/MXN-OTC': {
        'csv_path': f'{OTC_DATA_DIRECTORY}USD_MXN_OTC.csv',
        'timeframe': '1m',
        'description': 'US Dollar vs Mexican Peso (OTC)'
    },
    'USD/PEN-OTC': {
        'csv_path': f'{OTC_DATA_DIRECTORY}USD_PEN_OTC.csv',
        'timeframe': '1m',
        'description': 'US Dollar vs Peruvian Sol (OTC)'
    },
}

# Signal Configuration per Asset
SIGNAL_SETTINGS = {
    'min_confidence': 60,  # Minimum confidence threshold for signals
    'use_multiple_timeframes': False,  # Set to True for multi-timeframe analysis
    'export_results': True,  # Export results to JSON
}
