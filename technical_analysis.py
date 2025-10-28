import pandas as pd
import ta
from typing import Dict, Optional

class TechnicalAnalysis:
    def __init__(self, fast_period: int = 9, slow_period: int = 26):
        self.fast_period = fast_period
        self.slow_period = slow_period
    
    def calculate_emas(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate EMA indicators"""
        df = df.copy()
        
        # Calculate EMAs
        df['ema_fast'] = ta.trend.EMAIndicator(
            df['close'], window=self.fast_period
        ).ema_indicator()
        
        df['ema_slow'] = ta.trend.EMAIndicator(
            df['close'], window=self.slow_period
        ).ema_indicator()
        
        return df
    
    def analyze_ema_crossover(self, df: pd.DataFrame, symbol: str) -> Optional[Dict]:
        """Analyze EMA crossover for a symbol"""
        if len(df) < self.slow_period:
            return None
        
        df = self.calculate_emas(df)
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        
        # Determine signal
        signal = "Neutral"
        if latest['ema_fast'] > latest['ema_slow'] and prev['ema_fast'] <= prev['ema_slow']:
            signal = "🟢 BULLISH CROSS"
        elif latest['ema_fast'] < latest['ema_slow'] and prev['ema_fast'] >= prev['ema_slow']:
            signal = "🔴 BEARISH CROSS"
        elif latest['ema_fast'] > latest['ema_slow']:
            signal = "🟡 BULLISH (Recent)"
        elif latest['ema_fast'] < latest['ema_slow']:
            signal = "🟠 BEARISH (Recent)"
        
        return {
            'Symbol': symbol,
            'Price': latest['close'],
            f'EMA{self.fast_period}': latest['ema_fast'],
            f'EMA{self.slow_period}': latest['ema_slow'],
            'Signal': signal,
            'Trend': 'Bullish' if latest['ema_fast'] > latest['ema_slow'] else 'Bearish'
        }