import ccxt
import pandas as pd
from typing import List, Dict, Optional, Callable
import streamlit as st

class ExchangeClient:
    def __init__(self, exchange_name: str):
        self.exchange_name = exchange_name
        self.exchange = self._initialize_exchange()
    
    def _initialize_exchange(self):
        """Initialize exchange connection"""
        exchange_config = {
            'enableRateLimit': True,
            'sandbox': False,
        }
        
        if self.exchange_name == "binance":
            exchange_config['options'] = {'defaultType': 'future'}
            return ccxt.binance(exchange_config)
        elif self.exchange_name == "bybit":
            return ccxt.bybit(exchange_config)
        else:
            raise ValueError(f"Unsupported exchange: {self.exchange_name}")
    
    def fetch_markets(self) -> List[str]:
        """Fetch available futures markets"""
        try:
            markets = self.exchange.load_markets()
            futures_symbols = [
                symbol for symbol in markets.keys()
                if 'USDT' in symbol and '/USDT' in symbol and '.P' not in symbol
            ]
            return futures_symbols
        except Exception as e:
            st.error(f"Error fetching markets from {self.exchange_name}: {e}")
            return []
    
    def fetch_ohlcv(self, symbol: str, timeframe: str = '1h', limit: int = 100) -> Optional[pd.DataFrame]:
        """Fetch OHLCV data for a symbol"""
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            return df
        except Exception as e:
            st.warning(f"Could not fetch data for {symbol}: {e}")
            return None
    
    def scan_symbols(self, timeframe: str, max_symbols: int, analysis_function: Callable) -> List[Dict]:
        """Scan multiple symbols and return analysis results"""
        symbols = self.fetch_markets()
        
        if not symbols:
            return []
        
        # Limit symbols for performance
        symbols = symbols[:max_symbols]
        results = []
        
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, symbol in enumerate(symbols):
            status_text.text(f"Analyzing {symbol}... ({i+1}/{len(symbols)})")
            
            df = self.fetch_ohlcv(symbol, timeframe)
            if df is not None and len(df) > 50:  # Ensure enough data
                result = analysis_function(df, symbol)
                if result:
                    results.append(result)
            
            progress_bar.progress((i + 1) / len(symbols))
        
        status_text.text("Analysis complete!")
        return results