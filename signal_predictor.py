import pandas as pd
from indicators import TechnicalIndicators
from config import (
    RSI_OVERSOLD, RSI_OVERBOUGHT, OTC_ASSET_PAIRS, ASSET_PAIR_CONFIG, 
    SIGNAL_SETTINGS, LOOP_SETTINGS, NUMBER_OF_CANDLES
)
from datetime import datetime
import json

class SignalPredictor:
    """Predict buy/sell signals based on technical indicators for a single pair"""
    
    @staticmethod
    def predict_signal(df):
        """
        Generate trading signal based on 12 historical candles.
        
        Args:
            df: DataFrame with last 12 candles (OHLCV data)
            
        Returns:
            Dictionary with signal and confidence
        """
        if df is None or len(df) == 0:
            return {
                'signal': 'HOLD',
                'confidence': 0,
                'reason': 'No data available'
            }
        
        close_prices = pd.Series(df['close'].values)
        
        # Calculate all technical indicators
        rsi = TechnicalIndicators.calculate_rsi(close_prices)
        macd, signal_line, histogram = TechnicalIndicators.calculate_macd(close_prices)
        upper_bb, middle_bb, lower_bb = TechnicalIndicators.calculate_bollinger_bands(close_prices)
        momentum = TechnicalIndicators.calculate_momentum(close_prices)
        atr = TechnicalIndicators.calculate_atr(df)
        
        # Get current and previous price
        current_price = df['close'].iloc[-1]
        previous_price = df['close'].iloc[-2] if len(df) > 1 else current_price
        
        # Initialize signal scoring
        buy_score = 0
        sell_score = 0
        
        # ========== RSI ANALYSIS ==========
        if rsi is not None:
            if rsi < RSI_OVERSOLD:
                buy_score += 2
            elif rsi > RSI_OVERBOUGHT:
                sell_score += 2
            elif rsi < 50:
                buy_score += 1
            else:
                sell_score += 1
        
        # ========== MACD ANALYSIS ==========
        if macd is not None and signal_line is not None and histogram is not None:
            if histogram > 0 and macd > signal_line:
                buy_score += 2
            elif histogram < 0 and macd < signal_line:
                sell_score += 2
            elif histogram > 0:
                buy_score += 1
            else:
                sell_score += 1
        
        # ========== BOLLINGER BANDS ANALYSIS ==========
        if lower_bb is not None and upper_bb is not None:
            if current_price < lower_bb:
                buy_score += 2
            elif current_price > upper_bb:
                sell_score += 2
            elif current_price < middle_bb:
                buy_score += 1
            else:
                sell_score += 1
        
        # ========== MOMENTUM ANALYSIS ==========
        if momentum is not None:
            if momentum > 0:
                buy_score += 1
            else:
                sell_score += 1
        
        # ========== PRICE ACTION ANALYSIS ==========
        if current_price > previous_price:
            buy_score += 1
        else:
            sell_score += 1
        
        # Determine final signal and confidence
        total_score = buy_score + sell_score
        confidence = max(buy_score, sell_score) / total_score if total_score > 0 else 0
        
        if buy_score > sell_score:
            signal = 'BUY'
        elif sell_score > buy_score:
            signal = 'SELL'
        else:
            signal = 'HOLD'
        
        # Generate reason for the signal
        reason = SignalPredictor._generate_reason(rsi, macd, histogram, current_price, lower_bb, upper_bb, momentum)
        
        return {
            'signal': signal,
            'confidence': round(confidence * 100, 2),
            'reason': reason,
            'indicators': {
                'rsi': round(rsi, 2) if rsi is not None else None,
                'macd': round(macd, 6) if macd is not None else None,
                'macd_signal': round(signal_line, 6) if signal_line is not None else None,
                'macd_histogram': round(histogram, 6) if histogram is not None else None,
                'bb_upper': round(upper_bb, 6) if upper_bb is not None else None,
                'bb_middle': round(middle_bb, 6) if middle_bb is not None else None,
                'bb_lower': round(lower_bb, 6) if lower_bb is not None else None,
                'momentum': round(momentum, 6) if momentum is not None else None,
                'atr': round(atr, 6) if atr is not None else None,
                'current_price': round(current_price, 6)
            },
            'candle_count': len(df),
            'buy_score': buy_score,
            'sell_score': sell_score
        }
    
    @staticmethod
    def _generate_reason(rsi, macd, histogram, price, lower_bb, upper_bb, momentum):
        """
        Generate human-readable reason for the signal.
        """
        reasons = []
        
        if rsi is not None:
            if rsi < 30:
                reasons.append("RSI oversold")
            elif rsi > 70:
                reasons.append("RSI overbought")
        
        if histogram is not None and histogram > 0:
            reasons.append("MACD positive")
        elif histogram is not None:
            reasons.append("MACD negative")
        
        if lower_bb is not None and price < lower_bb:
            reasons.append("Price below lower BB")
        elif upper_bb is not None and price > upper_bb:
            reasons.append("Price above upper BB")
        
        if momentum is not None and momentum > 0:
            reasons.append("Positive momentum")
        elif momentum is not None:
            reasons.append("Negative momentum")
        
        return " | ".join(reasons) if reasons else "Neutral technical conditions"


class MultiPairSignalPredictor:
    """
    Predict signals for multiple OTC asset pairs.
    Loops through all configured pairs and generates signals for each.
    """
    
    def __init__(self):
        """Initialize the multi-pair predictor"""
        self.asset_pairs = OTC_ASSET_PAIRS
        self.pair_config = ASSET_PAIR_CONFIG
        self.results = []
        self.errors = []
        self.verbose = LOOP_SETTINGS.get('verbose_logging', True)
    
    def predict_all_pairs(self, data_loader):
        """
        Loop through all configured OTC asset pairs and generate signals.
        
        Args:
            data_loader: DataLoader instance for loading CSV data
            
        Returns:
            List of signal results for all pairs
        """
        self.results = []
        self.errors = []
        
        print("\n" + "="*80)
        print("QUOTEX SIGNAL BOT - MULTI-PAIR OTC ANALYSIS")
        print("="*80)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Total Pairs to Analyze: {len(self.asset_pairs)}")
        print("="*80)
        print()
        
        # Loop through each asset pair
        for idx, pair in enumerate(self.asset_pairs, 1):
            print(f"[{idx}/{len(self.asset_pairs)}] Processing: {pair}")
            print("-" * 80)
            
            try:
                pair_result = self._predict_pair(pair, data_loader)
                if pair_result:
                    self.results.append(pair_result)
                    print(f"  ✓ Complete")
                else:
                    print(f"  ✗ Failed to generate signal")
                    self.errors.append({'pair': pair, 'error': 'Failed to generate signal'})
            except Exception as e:
                error_msg = str(e)
                print(f"  ✗ Error: {error_msg}")
                self.errors.append({'pair': pair, 'error': error_msg})
                
                # Stop processing if configured
                if LOOP_SETTINGS.get('stop_on_error', False):
                    print("\n  Stopping processing due to error.")
                    break
            
            print()
        
        return self.results
    
    def _predict_pair(self, pair, data_loader):
        """
        Generate signal for a single OTC asset pair.
        
        Args:
            pair: Asset pair string (e.g., 'USD/ARS-OTC')
            data_loader: DataLoader instance
            
        Returns:
            Dictionary with pair signal result or None if failed
        """
        # Validate pair configuration exists
        if pair not in self.pair_config:
            print(f"  Configuration not found for {pair}")
            return None
        
        config = self.pair_config[pair]
        
        # Skip disabled pairs
        if not config.get('enabled', True):
            print(f"  Pair disabled in configuration")
            return None
        
        csv_path = config['csv_path']
        description = config['description']
        
        # Load CSV data for this pair
        candle_data = data_loader.load_csv(csv_path)
        if candle_data is None:
            print(f"  Cannot load CSV: {csv_path}")
            return None
        
        # Validate candlestick data
        if not data_loader.validate_candles(candle_data):
            print(f"  Invalid candlestick data")
            return None
        
        # Extract last 12 candles
        last_candles = data_loader.get_last_n_candles(candle_data, NUMBER_OF_CANDLES)
        if last_candles is None or len(last_candles) == 0:
            print(f"  No candle data available")
            return None
        
        # Generate signal for this pair
        signal_result = SignalPredictor.predict_signal(last_candles)
        
        # Build comprehensive result object
        pair_result = {
            'timestamp': datetime.now().isoformat(),
            'pair': pair,
            'description': description,
            'csv_path': csv_path,
            'timeframe': config['timeframe'],
            'signal': signal_result['signal'],
            'confidence': signal_result['confidence'],
            'reason': signal_result['reason'],
            'indicators': signal_result['indicators'],
            'candle_count': signal_result['candle_count'],
            'scores': {
                'buy': signal_result['buy_score'],
                'sell': signal_result['sell_score']
            },
            'last_candle_timestamp': str(last_candles['timestamp'].iloc[-1]) if 'timestamp' in last_candles.columns else None,
            'price_action': {
                'open': round(last_candles['open'].iloc[-1], config.get('decimal_places', 2)),
                'high': round(last_candles['high'].iloc[-1], config.get('decimal_places', 2)),
                'low': round(last_candles['low'].iloc[-1], config.get('decimal_places', 2)),
                'close': round(last_candles['close'].iloc[-1], config.get('decimal_places', 2)),
                'volume': round(last_candles['volume'].iloc[-1], 2)
            }
        }
        
        # Print result summary
        print(f"  Signal: {pair_result['signal']} (Confidence: {pair_result['confidence']}%)")
        print(f"  Reason: {pair_result['reason']}")
        print(f"  Price: {pair_result['price_action']['close']}")
        print(f"  Scores - Buy: {pair_result['scores']['buy']}, Sell: {pair_result['scores']['sell']}")
        
        return pair_result
    
    def get_summary(self):
        """
        Generate summary statistics for all analyzed pairs.
        
        Returns:
            Dictionary with signal summary
        """
        if not self.results:
            return {
                'total_pairs': len(self.asset_pairs),
                'analyzed_pairs': 0,
                'buy_signals': 0,
                'sell_signals': 0,
                'hold_signals': 0,
                'errors': len(self.errors),
                'strong_signals': [],
                'weak_signals': []
            }
        
        # Count signals
        buy_count = sum(1 for r in self.results if r['signal'] == 'BUY')
        sell_count = sum(1 for r in self.results if r['signal'] == 'SELL')
        hold_count = sum(1 for r in self.results if r['signal'] == 'HOLD')
        
        # Filter by confidence threshold
        min_confidence = SIGNAL_SETTINGS.get('min_confidence', 60)
        strong_signals = [r for r in self.results if r['confidence'] >= min_confidence]
        weak_signals = [r for r in self.results if r['confidence'] < min_confidence]
        
        return {
            'timestamp': datetime.now().isoformat(),
            'total_pairs': len(self.asset_pairs),
            'analyzed_pairs': len(self.results),
            'buy_signals': buy_count,
            'sell_signals': sell_count,
            'hold_signals': hold_count,
            'errors': len(self.errors),
            'strong_signals': [
                {
                    'pair': r['pair'],
                    'signal': r['signal'],
                    'confidence': r['confidence'],
                    'reason': r['reason'],
                    'price': r['price_action']['close']
                }
                for r in strong_signals
            ],
            'weak_signals': [
                {
                    'pair': r['pair'],
                    'signal': r['signal'],
                    'confidence': r['confidence'],
                    'price': r['price_action']['close']
                }
                for r in weak_signals
            ]
        }
    
    def export_results(self, output_file=None):
        """
        Export all results and summary to JSON file.
        
        Args:
            output_file: Output file path (optional)
            
        Returns:
            Path to the exported file
        """
        if output_file is None:
            output_file = f"otc_signals_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        export_data = {
            'summary': self.get_summary(),
            'detailed_results': self.results,
            'errors': self.errors
        }
        
        with open(output_file, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        return output_file
    
    def print_summary(self):
        """
        Print formatted summary of all signals to console.
        """
        summary = self.get_summary()
        min_confidence = SIGNAL_SETTINGS.get('min_confidence', 60)
        
        print("\n" + "="*80)
        print("SIGNAL SUMMARY")
        print("="*80)
        print(f"Total Pairs:      {summary['total_pairs']}")
        print(f"Analyzed:         {summary['analyzed_pairs']}")
        print(f"Errors:           {summary['errors']}")
        print(f"BUY Signals:      {summary['buy_signals']}")
        print(f"SELL Signals:     {summary['sell_signals']}")
        print(f"HOLD Signals:     {summary['hold_signals']}")
        print("="*80)
        print()
        
        # Display strong signals
        if summary['strong_signals']:
            print(f"Strong Signals (Confidence >= {min_confidence}%):")
            print("-" * 80)
            for signal in summary['strong_signals']:
                print(f"  {signal['pair']:<15} | {signal['signal']:<5} | {signal['confidence']:>6.1f}% | Price: {signal['price']}")
                print(f"    └─ {signal['reason']}")
            print()
        
        # Display weak signals
        if summary['weak_signals']:
            print(f"Weak Signals (Confidence < {min_confidence}%):")
            print("-" * 80)
            for signal in summary['weak_signals']:
                print(f"  {signal['pair']:<15} | {signal['signal']:<5} | {signal['confidence']:>6.1f}% | Price: {signal['price']}")
            print()
        
        # Display errors if any
        if self.errors:
            print("Errors:")
            print("-" * 80)
            for error in self.errors:
                print(f"  {error['pair']}: {error['error']}")
            print()
        
        print("="*80)
    
    def print_detailed_results(self):
        """
        Print detailed results for all pairs.
        """
        if not self.results:
            print("No results to display.")
            return
        
        print("\n" + "="*80)
        print("DETAILED RESULTS")
        print("="*80)
        
        for result in self.results:
            print(f"\nPair: {result['pair']}")
            print(f"Description: {result['description']}")
            print(f"Signal: {result['signal']} ({result['confidence']}%)")
            print(f"Reason: {result['reason']}")
            print(f"Price: O:{result['price_action']['open']} H:{result['price_action']['high']} L:{result['price_action']['low']} C:{result['price_action']['close']}")
            print(f"Indicators: RSI={result['indicators']['rsi']} MACD={result['indicators']['macd']} ATR={result['indicators']['atr']}")
            print("-" * 80)
