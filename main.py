import streamlit as st
import pandas as pd
import ccxt
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Configure the app
st.set_page_config(
    page_title="Crypto Futures Screener",
    page_icon="📈",
    layout="wide"
)

def calculate_ema(data, period):
    """Calculate EMA using pandas (built-in, no external dependencies)"""
    return data.ewm(span=period, adjust=False).mean()

def main():
    st.title("🚀 Crypto Futures Screener")
    st.markdown("EMA Crossover Scanner for Binance & Bybit")
    
    # Sidebar configuration
    st.sidebar.header("Settings")
    
    exchange_name = st.sidebar.selectbox("Exchange", ["binance", "bybit"])
    ema_fast = st.sidebar.number_input("Fast EMA", value=9, min_value=1, max_value=50)
    ema_slow = st.sidebar.number_input("Slow EMA", value=26, min_value=5, max_value=100)
    timeframe = st.sidebar.selectbox("Timeframe", ["1h", "4h", "1d", "1w"])
    max_symbols = st.sidebar.slider("Max Symbols", 10, 600, 100)
    
    if st.button("🔍 SCAN MARKETS"):
        scan_markets(exchange_name, ema_fast, ema_slow, timeframe, max_symbols)

def scan_markets(exchange_name, ema_fast, ema_slow, timeframe, max_symbols):
    """Scan markets with error handling"""
    try:
        # Initialize exchange
        if exchange_name == "binance":
            exchange = ccxt.binance({
                'enableRateLimit': True,
                'options': {'defaultType': 'future'}
            })
        else:
            exchange = ccxt.bybit({'enableRateLimit': True})
        
        # Get markets
        st.info(f"🔄 Loading markets from {exchange_name}...")
        markets = exchange.load_markets()
        symbols = [s for s in markets.keys() if 'USDT' in s and '/USDT' in s][:max_symbols]
        
        st.info(f"📊 Scanning {len(symbols)} symbols on {timeframe} timeframe...")
        
        results = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, symbol in enumerate(symbols):
            status_text.text(f"Analyzing {symbol}... ({i+1}/{len(symbols)})")
            
            try:
                # Fetch OHLCV data
                ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=100)
                if len(ohlcv) > ema_slow:
                    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                    
                    # Calculate EMAs using pandas built-in
                    df['ema_fast'] = calculate_ema(df['close'], ema_fast)
                    df['ema_slow'] = calculate_ema(df['close'], ema_slow)
                    
                    latest = df.iloc[-1]
                    prev = df.iloc[-2]
                    
                    # Determine signal
                    signal = "Neutral"
                    if latest['ema_fast'] > latest['ema_slow'] and prev['ema_fast'] <= prev['ema_slow']:
                        signal = "🟢 BULLISH CROSS"
                    elif latest['ema_fast'] < latest['ema_slow'] and prev['ema_fast'] >= prev['ema_slow']:
                        signal = "🔴 BEARISH CROSS"
                    elif latest['ema_fast'] > latest['ema_slow']:
                        signal = "🟡 BULLISH Trend"
                    elif latest['ema_fast'] < latest['ema_slow']:
                        signal = "🟠 BEARISH Trend"
                    
                    results.append({
                        'Symbol': symbol,
                        'Price': latest['close'],
                        f'EMA{ema_fast}': latest['ema_fast'],
                        f'EMA{ema_slow}': latest['ema_slow'],
                        'Signal': signal,
                        'Trend': 'Bullish' if latest['ema_fast'] > latest['ema_slow'] else 'Bearish'
                    })
                
            except Exception as e:
                continue  # Skip symbols with errors
            
            progress_bar.progress((i + 1) / len(symbols))
        
        # Display results
        if results:
            df_results = pd.DataFrame(results)
            
            # Summary
            bullish = len([r for r in results if 'BULLISH' in r['Signal']])
            bearish = len([r for r in results if 'BEARISH' in r['Signal']])
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Scanned", len(symbols))
            col2.metric("Signals Found", len(results))
            col3.metric("Bullish/Bearish", f"{bullish}/{bearish}")
            
            # Filter options
            st.subheader("📊 Results")
            col1, col2 = st.columns(2)
            with col1:
                show_signals = st.multiselect(
                    "Filter by Signal",
                    options=df_results['Signal'].unique(),
                    default=df_results['Signal'].unique()
                )
            with col2:
                show_trend = st.multiselect(
                    "Filter by Trend", 
                    options=df_results['Trend'].unique(),
                    default=df_results['Trend'].unique()
                )
            
            filtered_df = df_results[
                (df_results['Signal'].isin(show_signals)) & 
                (df_results['Trend'].isin(show_trend))
            ]
            
            st.dataframe(
                filtered_df.style.format({
                    'Price': '{:.6f}',
                    f'EMA{ema_fast}': '{:.6f}',
                    f'EMA{ema_slow}': '{:.6f}'
                }),
                use_container_width=True
            )
            
            # Chart for selected symbol
            if not filtered_df.empty:
                st.subheader("📈 Detailed Chart")
                selected_symbol = st.selectbox("Select symbol:", filtered_df['Symbol'].tolist())
                
                if selected_symbol:
                    try:
                        ohlcv = exchange.fetch_ohlcv(selected_symbol, timeframe, limit=100)
                        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                        df['ema_fast'] = calculate_ema(df['close'], ema_fast)
                        df['ema_slow'] = calculate_ema(df['close'], ema_slow)
                        
                        # Create chart
                        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                                          vertical_spacing=0.1, row_heights=[0.7, 0.3])
                        
                        # Candlestick
                        fig.add_trace(go.Candlestick(
                            x=df['timestamp'], open=df['open'], high=df['high'],
                            low=df['low'], close=df['close'], name='Price'
                        ), row=1, col=1)
                        
                        # EMAs
                        fig.add_trace(go.Scatter(
                            x=df['timestamp'], y=df['ema_fast'], 
                            line=dict(color='orange', width=1.5), name=f'EMA{ema_fast}'
                        ), row=1, col=1)
                        
                        fig.add_trace(go.Scatter(
                            x=df['timestamp'], y=df['ema_slow'], 
                            line=dict(color='blue', width=1.5), name=f'EMA{ema_slow}'
                        ), row=1, col=1)
                        
                        # Volume
                        colors = ['red' if close < open else 'green' 
                                for close, open in zip(df['close'], df['open'])]
                        fig.add_trace(go.Bar(
                            x=df['timestamp'], y=df['volume'], marker_color=colors, name='Volume'
                        ), row=2, col=1)
                        
                        fig.update_layout(height=600, title_text=f"{selected_symbol} - {timeframe}",
                                        xaxis_rangeslider_visible=False)
                        st.plotly_chart(fig, use_container_width=True)
                        
                    except Exception as e:
                        st.error(f"Error loading chart: {e}")
            
        else:
            st.warning("❌ No trading signals found. Try increasing the symbol limit.")
            
    except Exception as e:
        st.error(f"🚨 Error: {str(e)}")
        st.info("This might be a temporary network issue. Please try again.")

if __name__ == "__main__":
    main()
