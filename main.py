import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Import from current directory instead of app package
from exchange_client import ExchangeClient
from technical_analysis import TechnicalAnalysis
from utils import format_number, validate_settings

# Configure the app
st.set_page_config(
    page_title="Crypto Futures Screener",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Default settings
DEFAULT_SETTINGS = {
    "EXCHANGES": ["binance", "bybit"],
    "EMA_FAST": 9,
    "EMA_SLOW": 26,
    "MAX_SYMBOLS": 50,
    "TIMEFRAMES": ["1m", "5m", "15m", "1h", "4h", "1d", "1w"],
    "DEFAULT_TIMEFRAME": "1h",
    "OHLCV_LIMIT": 100
}

def main():
    # Title and description
    st.title("🚀 Crypto Futures Screener")
    st.markdown("Scan for EMA crossover opportunities across multiple exchanges")
    
    # Sidebar configuration
    settings = render_sidebar()
    
    # Main content
    if st.button("🔍 SCAN MARKETS", type="primary", use_container_width=True):
        scan_markets(settings)
    
    # Instructions
    render_instructions()

def render_sidebar():
    """Render sidebar with configuration options"""
    st.sidebar.header("⚙️ Configuration")
    
    # Exchange selection
    exchange_name = st.sidebar.selectbox(
        "Select Exchange",
        DEFAULT_SETTINGS["EXCHANGES"],
        index=0
    )
    
    # EMA configuration
    st.sidebar.subheader("📊 EMA Settings")
    col1, col2 = st.sidebar.columns(2)
    with col1:
        ema_fast = st.number_input(
            "Fast EMA", 
            min_value=1, 
            max_value=100, 
            value=DEFAULT_SETTINGS["EMA_FAST"]
        )
    with col2:
        ema_slow = st.number_input(
            "Slow EMA", 
            min_value=1, 
            max_value=200, 
            value=DEFAULT_SETTINGS["EMA_SLOW"]
        )
    
    # Timeframe selection
    timeframe = st.sidebar.selectbox(
        "Select Timeframe",
        DEFAULT_SETTINGS["TIMEFRAMES"],
        index=3  # Default to 1h
    )
    
    # Performance settings
    st.sidebar.subheader("⚡ Performance")
    max_symbols = st.sidebar.slider(
        "Max Symbols to Scan",
        min_value=10,
        max_value=100,
        value=DEFAULT_SETTINGS["MAX_SYMBOLS"],
        help="Limit number of symbols for faster scanning"
    )
    
    return {
        "exchange": exchange_name,
        "ema_fast": ema_fast,
        "ema_slow": ema_slow,
        "timeframe": timeframe,
        "max_symbols": max_symbols
    }

def scan_markets(settings):
    """Scan markets based on settings"""
    # Validate settings
    if not validate_settings(settings):
        st.error("Invalid settings. Please check your inputs.")
        return
    
    # Initialize clients
    exchange_client = ExchangeClient(settings["exchange"])
    tech_analysis = TechnicalAnalysis(
        fast_period=settings["ema_fast"],
        slow_period=settings["ema_slow"]
    )
    
    # Show progress
    st.info(f"🔄 Scanning {settings['exchange'].upper()} futures markets on {settings['timeframe']} timeframe...")
    
    try:
        # Fetch and analyze symbols
        results = exchange_client.scan_symbols(
            timeframe=settings["timeframe"],
            max_symbols=settings["max_symbols"],
            analysis_function=tech_analysis.analyze_ema_crossover
        )
        
        if results:
            display_results(results, settings)
        else:
            st.warning("❌ No trading signals found or error fetching data.")
            
    except Exception as e:
        st.error(f"🚨 Error during scanning: {str(e)}")

def display_results(results, settings):
    """Display scan results"""
    st.subheader("📊 Scan Results")
    
    # Convert to DataFrame
    df = pd.DataFrame(results)
    
    # Filter options
    col1, col2 = st.columns(2)
    with col1:
        show_signals = st.multiselect(
            "Filter by Signal",
            options=df['Signal'].unique(),
            default=df['Signal'].unique()
        )
    with col2:
        show_trend = st.multiselect(
            "Filter by Trend",
            options=df['Trend'].unique(),
            default=df['Trend'].unique()
        )
    
    # Filter results
    filtered_df = df[
        (df['Signal'].isin(show_signals)) & 
        (df['Trend'].isin(show_trend))
    ]
    
    if filtered_df.empty:
        st.warning("No results match your filters.")
        return
    
    # Display results table
    st.dataframe(
        filtered_df.style.format({
            'Price': '{:.6f}',
            f'EMA{settings["ema_fast"]}': '{:.6f}',
            f'EMA{settings["ema_slow"]}': '{:.6f}'
        }),
        use_container_width=True,
        height=400
    )
    
    # Detailed analysis for selected symbol
    if not filtered_df.empty:
        display_detailed_analysis(filtered_df, settings)

def display_detailed_analysis(results_df, settings):
    """Display detailed analysis for selected symbol"""
    st.subheader("📈 Detailed Analysis")
    
    selected_symbol = st.selectbox(
        "Select symbol for detailed chart:",
        results_df['Symbol'].tolist()
    )
    
    if selected_symbol:
        try:
            # Fetch detailed data
            exchange_client = ExchangeClient(settings["exchange"])
            ohlcv_data = exchange_client.fetch_ohlcv(
                symbol=selected_symbol,
                timeframe=settings["timeframe"],
                limit=100
            )
            
            if ohlcv_data is not None:
                # Calculate EMAs
                tech_analysis = TechnicalAnalysis(
                    fast_period=settings["ema_fast"],
                    slow_period=settings["ema_slow"]
                )
                df = tech_analysis.calculate_emas(ohlcv_data)
                
                # Create chart
                fig = create_price_chart(df, selected_symbol, settings)
                st.plotly_chart(fig, use_container_width=True)
                
                # Show metrics
                display_metrics(df, settings)
                
        except Exception as e:
            st.error(f"Error fetching detailed data: {str(e)}")

def create_price_chart(df, symbol, settings):
    """Create interactive price chart with EMAs"""
    fig = make_subplots(
        rows=2, 
        cols=1, 
        shared_xaxes=True,
        vertical_spacing=0.1,
        subplot_titles=(
            f'{symbol} Price Chart - {settings["timeframe"]}', 
            'Volume'
        ),
        row_heights=[0.7, 0.3]
    )
    
    # Candlestick chart
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name='Price'
        ),
        row=1, col=1
    )
    
    # EMAs
    fig.add_trace(
        go.Scatter(
            x=df.index, 
            y=df['ema_fast'], 
            line=dict(color='orange', width=1.5),
            name=f'EMA{settings["ema_fast"]}'
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=df.index, 
            y=df['ema_slow'], 
            line=dict(color='blue', width=1.5),
            name=f'EMA{settings["ema_slow"]}'
        ),
        row=1, col=1
    )
    
    # Volume
    colors = ['red' if close < open else 'green' 
              for close, open in zip(df['close'], df['open'])]
    fig.add_trace(
        go.Bar(
            x=df.index, 
            y=df['volume'],
            marker_color=colors,
            name='Volume'
        ),
        row=2, col=1
    )
    
    fig.update_layout(
        height=600,
        title_text=f"Technical Analysis - {symbol}",
        xaxis_rangeslider_visible=False,
        showlegend=True
    )
    
    return fig

def display_metrics(df, settings):
    """Display current metrics"""
    latest = df.iloc[-1]
    
    col1, col2, col3, col4 = st.columns(4)
    
    col1.metric(
        "Current Price", 
        f"{latest['close']:.6f}"
    )
    col2.metric(
        f"EMA{settings['ema_fast']}", 
        f"{latest['ema_fast']:.6f}"
    )
    col3.metric(
        f"EMA{settings['ema_slow']}", 
        f"{latest['ema_slow']:.6f}"
    )
    
    trend_color = "🟢" if latest['ema_fast'] > latest['ema_slow'] else "🔴"
    trend_text = "Bullish" if latest['ema_fast'] > latest['ema_slow'] else "Bearish"
    col4.metric("Trend", f"{trend_color} {trend_text}")

def render_instructions():
    """Render usage instructions"""
    with st.expander("ℹ️ How to use this screener"):
        st.markdown("""
        ### Usage Guide:
        1. **Select Exchange**: Choose between Binance or Bybit
        2. **Configure EMA**: Set your preferred fast and slow EMA periods
        3. **Choose Timeframe**: Select the chart timeframe for analysis
        4. **Adjust Performance**: Set maximum symbols to scan
        5. **Click SCAN**: Analyze markets for EMA crossovers
        
        ### Signal Types:
        - 🟢 **BULLISH CROSS**: Golden cross detected in current candle
        - 🔴 **BEARISH CROSS**: Death cross detected in current candle  
        - 🟡 **BULLISH (Recent)**: Recently had a golden cross
        - 🟠 **BEARISH (Recent)**: Recently had a death cross
        - **Neutral**: No recent crossover
        
        ### Tips:
        - Start with fewer symbols for faster results
        - Use 1h/4h timeframes for more reliable signals
        - Combine with other indicators for confirmation
        """)

if __name__ == "__main__":
    main()