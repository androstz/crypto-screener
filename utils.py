import streamlit as st
from typing import Dict, Any

def format_number(value: float, decimals: int = 6) -> str:
    """Format number with specified decimals"""
    return f"{value:.{decimals}f}"

def validate_settings(settings: Dict[str, Any]) -> bool:
    """Validate user settings"""
    if settings['ema_fast'] >= settings['ema_slow']:
        st.error("Fast EMA must be smaller than Slow EMA")
        return False
    
    if settings['max_symbols'] < 1:
        st.error("Max symbols must be at least 1")
        return False
    
    return True

def calculate_percentage_change(current: float, previous: float) -> float:
    """Calculate percentage change"""
    if previous == 0:
        return 0
    return ((current - previous) / previous) * 100