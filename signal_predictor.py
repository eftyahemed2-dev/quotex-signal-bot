import pandas as pd
from indicators import TechnicalIndicators
from config import RSI_OVERSOLD, RSI_OVERBOUGHT, OTC_ASSET_PAIRS, ASSET_PAIR_CONFIG, SIGNAL_SETTINGS
from datetime import datetime
import json

class SignalPredictor:
    """Predict buy/sell signals based on technical indicators"""
    
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
        
        # Calculate indicators
        rsi = TechnicalIndicators.calculate_rsi(close_prices)
        macd, signal_line, histogram = TechnicalIndicators.calculate_macd(close_prices)
        upper_bb, middle_bb, lower_bb = TechnicalIndicators.calculate_bollinger_bands(close_prices)
        momentum = TechnicalIndicators.calculate_momentum(close_prices)
        atr = TechnicalIndicators.calculate_atr(df)
        
        # Get current price
        current_price = df['close'].iloc[-1]
        previous_price = df['close'].iloc[-2] if len(df) > 1 else current_price
        
        # Initialize signal scoring
        buy_score = 0
        sell_score = 0
        
        # RSI Analysis
        if rsi is not None:
            if rsi < RSI_OVERSOLD:
                buy_score += 2
            elif rsi > RSI_OVERBOUGHT:
                sell_score += 2
            elif rsi < 50:
                buy_score += 1
            else:
                sell_score += 1
        
        # MACD Analysis
        if macd is not None and signal_line is not None and histogram is not None:
            if histogram > 0 and macd > signal_line:
                buy_score += 2
            elif histogram < 0 and macd < signal_line:
                sell_score += 2
            elif histogram > 0:
                buy_score += 1
            else:
                sell_score += 1
        
        # Bollinger Bands Analysis
        if lower_bb is not None and upper_bb is not None:
            if current_price < lower_bb:
                buy_score += 2
            elif current_price > upper_bb:
                sell_score += 2
            elif current_price < middle_bb:
                buy_score += 1
            else:
                sell_score += 1
        
        # Momentum Analysis
        if momentum is not None:
            if momentum > 0:
                buy_score += 1
            else:
                sell_score += 1
        
        # Price Action Analysis
        if current_price > previous_price:
            buy_score += 1
        else:
            sell_score += 1
        
        # Determine signal and confidence
        total_score = buy_score + sell_score
        confidence = max(buy_score, sell_score) / total_score if total_score > 0 else 0
        
        if buy_score > sell_score:
            signal = 'BUY'
        elif sell_score > buy_score:
            signal = 'SELL'
        else:
            signal = 'HOLD'
        
        # Generate reason
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
            reasons.append("Price below lower Bollinger Band")
        elif upper_bb is not None and price > upper_bb:
            reasons.append("Price above upper Bollinger Band")
        
        if momentum is not None and momentum > 0:
            reasons.append("Positive momentum")
        elif momentum is not None:
            reasons.append("Negative momentum")
        
        return " | ".join(reasons) if reasons else "Neutral technical conditions"


class MultiPairSignalPredictor:
    """Predict signals for multiple OTC asset pairs"""
    
    def __init__(self):
        """Initialize the multi-pair predictor"""
        self.asset_pairs = OTC_ASSET_PAIRS
        self.pair_config = ASSET_PAIR_CONFIG
        self.results = []
    
    def predict_all_pairs(self, data_loader):
        """
        Generate signals for all configured OTC asset pairs.
        
        Args:
            data_loader: DataLoader instance for loading CSV data
            
        Returns:
            List of signal results for all pairs
        """
        self.results = []
        
        print("=" * 80)
        print("Multi-Pair OTC Signal Analysis")
        print("=" * 80)
        print(f"Analyzing {len(self.asset_pairs)} asset pairs...")
        print()
        
        for pair in self.asset_pairs:
            pair_result = self._predict_pair(pair, data_loader)
            if pair_result:
                self.results.append(pair_result)
        
        return self.results
    
    def _predict_pair(self, pair, data_loader):
        """
        Generate signal for a single asset pair.
        
        Args:
            pair: Asset pair string (e.g., 'USD/ARS-OTC')
            data_loader: DataLoader instance
            
        Returns:
            Dictionary with pair signal result or None if failed
        """
        print(f"Processing: {pair}")
        print("-" * 80)
        
        # Get pair configuration
        if pair not in self.pair_config:
            print(f"  ✗ Pair configuration not found for {pair}")
            print()
            return None
        
        config = self.pair_config[pair]
        csv_path = config['csv_path']
        description = config['description']
        
        # Load data for this pair
        candle_data = data_loader.load_csv(csv_path)
        
        if candle_data is None:
            print(f"  ✗ Failed to load data from {csv_path}")
            print()
            return None
        
        # Validate data
        if not data_loader.validate_candles(candle_data):
            print(f"  ✗ Invalid candlestick data for {pair}")
            print()
            return None
        
        # Get last 12 candles
        last_candles = data_loader.get_last_n_candles(candle_data, 12)
        
        if last_candles is None or len(last_candles) == 0:
            print(f"  ✗ No candle data available for {pair}")
            print()
            return None
        
        # Generate signal
        signal_result = SignalPredictor.predict_signal(last_candles)
        
        # Create pair result object
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
                'open': round(last_candles['open'].iloc[-1], 8),
                'high': round(last_candles['high'].iloc[-1], 8),
                'low': round(last_candles['low'].iloc[-1], 8),
                'close': round(last_candles['close'].iloc[-1], 8),
                'volume': round(last_candles['volume'].iloc[-1], 2)
            }
        }
        
        # Display result
        print(f"  Signal: {pair_result['signal']} (Confidence: {pair_result['confidence']}%)")
        print(f"  Reason: {pair_result['reason']}")
        print(f"  Price: {pair_result['price_action']['close']}")
        print()
        
        return pair_result
    
    def get_summary(self):
        """
        Get a summary of all signals.
        
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
                'strong_signals': [],
                'weak_signals': []
            }
        
        buy_count = sum(1 for r in self.results if r['signal'] == 'BUY')
        sell_count = sum(1 for r in self.results if r['signal'] == 'SELL')
        hold_count = sum(1 for r in self.results if r['signal'] == 'HOLD')
        
        # Filter strong signals (confidence >= SIGNAL_SETTINGS['min_confidence'])
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
            'strong_signals': [
                {
                    'pair': r['pair'],
                    'signal': r['signal'],
                    'confidence': r['confidence'],
                    'reason': r['reason']
                }
                for r in strong_signals
            ],
            'weak_signals': [
                {
                    'pair': r['pair'],
                    'signal': r['signal'],
                    'confidence': r['confidence']
                }
                for r in weak_signals
            ]
        }
    
    def export_results(self, output_file=None):
        """
        Export results to JSON file.
        
        Args:
            output_file: Output file path (optional)
        """
        if output_file is None:
            output_file = f"otc_signals_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        export_data = {
            'summary': self.get_summary(),
            'detailed_results': self.results
        }
        
        with open(output_file, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        return output_file
    
    def print_summary(self):
        """Print a formatted summary of all signals"""
        summary = self.get_summary()
        
        print("=" * 80)
        print("SIGNAL SUMMARY")
        print("=" * 80)
        print(f"Total Pairs:      {summary['total_pairs']}")
        print(f"Analyzed Pairs:   {summary['analyzed_pairs']}")
        print(f"BUY Signals:      {summary['buy_signals']}")
        print(f"SELL Signals:     {summary['sell_signals']}")
        print(f"HOLD Signals:     {summary['hold_signals']}")
        print()
        
        min_confidence = SIGNAL_SETTINGS.get('min_confidence', 60)
        
        if summary['strong_signals']:
            print(f"Strong Signals (Confidence >= {min_confidence}%):")
            print("-" * 80)
            for signal in summary['strong_signals']:
                print(f"  {signal['pair']}: {signal['signal']} ({signal['confidence']}%)")
                print(f"    {signal['reason']}")
            print()
        
        if summary['weak_signals']:
            print(f"Weak Signals (Confidence < {min_confidence}%):")
            print("-" * 80)
            for signal in summary['weak_signals']:
                print(f"  {signal['pair']}: {signal['signal']} ({signal['confidence']}%)")
            print()
        
        print("=" * 80)
