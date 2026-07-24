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

# ============================================
# OTC ASSET PAIRS CONFIGURATION
# ============================================

# List of OTC asset pairs to analyze
OTC_ASSET_PAIRS = [
    'USD/ARS-OTC',
    'USD/COP-OTC',
    'USD/BRL-OTC',
    'USD/MXN-OTC',
    'USD/PEN-OTC',
]

# OTC Asset Data Directory
OTC_DATA_DIRECTORY = 'data/otc/'

# Detailed configuration for each OTC asset pair
# Each pair maps to its CSV file location and metadata
ASSET_PAIR_CONFIG = {
    'USD/ARS-OTC': {
        'csv_path': f'{OTC_DATA_DIRECTORY}USD_ARS_OTC.csv',
        'timeframe': '1m',
        'description': 'US Dollar vs Argentine Peso (OTC)',
        'decimal_places': 2,
        'enabled': True
    },
    'USD/COP-OTC': {
        'csv_path': f'{OTC_DATA_DIRECTORY}USD_COP_OTC.csv',
        'timeframe': '1m',
        'description': 'US Dollar vs Colombian Peso (OTC)',
        'decimal_places': 0,
        'enabled': True
    },
    'USD/BRL-OTC': {
        'csv_path': f'{OTC_DATA_DIRECTORY}USD_BRL_OTC.csv',
        'timeframe': '1m',
        'description': 'US Dollar vs Brazilian Real (OTC)',
        'decimal_places': 2,
        'enabled': True
    },
    'USD/MXN-OTC': {
        'csv_path': f'{OTC_DATA_DIRECTORY}USD_MXN_OTC.csv',
        'timeframe': '1m',
        'description': 'US Dollar vs Mexican Peso (OTC)',
        'decimal_places': 2,
        'enabled': True
    },
    'USD/PEN-OTC': {
        'csv_path': f'{OTC_DATA_DIRECTORY}USD_PEN_OTC.csv',
        'timeframe': '1m',
        'description': 'US Dollar vs Peruvian Sol (OTC)',
        'decimal_places': 2,
        'enabled': True
    },
}

# ============================================
# SIGNAL SETTINGS
# ============================================

SIGNAL_SETTINGS = {
    'min_confidence': 60,              # Minimum confidence threshold for strong signals
    'use_multiple_timeframes': False,  # Set to True for multi-timeframe analysis
    'export_results': True,            # Export results to JSON file
    'export_format': 'json',           # Export format: 'json', 'csv'
    'display_detailed': False,         # Display detailed indicator values
}

# ============================================
# LOOP PROCESSING CONFIGURATION
# ============================================

LOOP_SETTINGS = {
    'process_all_pairs': True,         # Process all enabled pairs
    'stop_on_error': False,            # Stop processing if any pair fails
    'parallel_processing': False,      # Process pairs in parallel (experimental)
    'verbose_logging': True,           # Enable verbose logging
}
