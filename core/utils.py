"""
Utility functions for stock data processing and screening
"""
import os
import pandas as pd
import numpy as np
from django.conf import settings
from datetime import datetime, timedelta

def get_stock_data_dir():
    """Get the stock data directory path"""
    return os.path.join(settings.BASE_DIR, 'stock_data')

def load_stock_data(symbol):
    """
    Load stock data from CSV file
    Returns DataFrame with columns: Date, Open, High, Low, Close, Volume
    """
    data_dir = get_stock_data_dir()
    filename = f"{symbol}.csv"
    filepath = os.path.join(data_dir, filename)
    
    if not os.path.exists(filepath):
        return None
    
    try:
        df = pd.read_csv(filepath, index_col=0, parse_dates=True)
        return df
    except Exception as e:
        print(f"Error loading {symbol}: {e}")
        return None

def get_available_stocks():
    """Get list of all available stock symbols"""
    data_dir = get_stock_data_dir()
    if not os.path.exists(data_dir):
        return []
    
    stocks = []
    for filename in os.listdir(data_dir):
        if filename.endswith('.csv'):
            symbol = filename.replace('.csv', '')
            stocks.append(symbol)
    
    return sorted(stocks)

def calculate_indicators(df):
    """
    Calculate technical indicators for a stock
    Returns a dictionary with various metrics
    """
    if df is None or df.empty:
        return None
    
    try:
        # Ensure we have required columns
        if 'Close' not in df.columns:
            return None
        
        close = df['Close']
        high = df['High'] if 'High' in df.columns else close
        low = df['Low'] if 'Low' in df.columns else close
        volume = df['Volume'] if 'Volume' in df.columns else pd.Series([0] * len(df))
        
        # Current price
        current_price = close.iloc[-1]
        
        # Price change (1D, 1W, 1M, 3M, 6M, 1Y)
        price_1d = close.iloc[-1] - close.iloc[-2] if len(close) > 1 else 0
        pct_1d = (price_1d / close.iloc[-2] * 100) if len(close) > 1 and close.iloc[-2] != 0 else 0
        
        price_1w = close.iloc[-1] - close.iloc[-6] if len(close) > 6 else 0
        pct_1w = (price_1w / close.iloc[-6] * 100) if len(close) > 6 and close.iloc[-6] != 0 else 0
        
        price_1m = close.iloc[-1] - close.iloc[-21] if len(close) > 21 else 0
        pct_1m = (price_1m / close.iloc[-21] * 100) if len(close) > 21 and close.iloc[-21] != 0 else 0
        
        price_3m = close.iloc[-1] - close.iloc[-63] if len(close) > 63 else 0
        pct_3m = (price_3m / close.iloc[-63] * 100) if len(close) > 63 and close.iloc[-63] != 0 else 0
        
        price_6m = close.iloc[-1] - close.iloc[-126] if len(close) > 126 else 0
        pct_6m = (price_6m / close.iloc[-126] * 100) if len(close) > 126 and close.iloc[-126] != 0 else 0
        
        price_1y = close.iloc[-1] - close.iloc[-252] if len(close) > 252 else 0
        pct_1y = (price_1y / close.iloc[-252] * 100) if len(close) > 252 and close.iloc[-252] != 0 else 0
        
        # Moving Averages
        ma_20 = close.rolling(window=20).mean().iloc[-1] if len(close) >= 20 else None
        ma_50 = close.rolling(window=50).mean().iloc[-1] if len(close) >= 50 else None
        ma_200 = close.rolling(window=200).mean().iloc[-1] if len(close) >= 200 else None
        
        # RSI (Relative Strength Index)
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        rsi_current = rsi.iloc[-1] if len(rsi) > 0 and not pd.isna(rsi.iloc[-1]) else None
        
        # Volatility (30-day)
        returns = close.pct_change()
        volatility_30d = returns.rolling(window=30).std().iloc[-1] * np.sqrt(252) * 100 if len(returns) >= 30 else None
        
        # Volume metrics
        avg_volume_20d = volume.rolling(window=20).mean().iloc[-1] if len(volume) >= 20 else None
        current_volume = volume.iloc[-1] if len(volume) > 0 else 0
        volume_ratio = (current_volume / avg_volume_20d) if avg_volume_20d and avg_volume_20d > 0 else None
        
        # High/Low
        high_52w = high.rolling(window=252).max().iloc[-1] if len(high) >= 252 else high.max()
        low_52w = low.rolling(window=252).min().iloc[-1] if len(low) >= 252 else low.min()
        
        # Distance from 52W high/low
        dist_from_high = ((current_price - high_52w) / high_52w * 100) if high_52w > 0 else None
        dist_from_low = ((current_price - low_52w) / low_52w * 100) if low_52w > 0 else None
        
        return {
            'current_price': round(current_price, 2),
            'price_1d': round(price_1d, 2),
            'pct_1d': round(pct_1d, 2),
            'price_1w': round(price_1w, 2),
            'pct_1w': round(pct_1w, 2),
            'price_1m': round(price_1m, 2),
            'pct_1m': round(pct_1m, 2),
            'price_3m': round(price_3m, 2),
            'pct_3m': round(pct_3m, 2),
            'price_6m': round(price_6m, 2),
            'pct_6m': round(pct_6m, 2),
            'price_1y': round(price_1y, 2),
            'pct_1y': round(pct_1y, 2),
            'ma_20': round(ma_20, 2) if ma_20 else None,
            'ma_50': round(ma_50, 2) if ma_50 else None,
            'ma_200': round(ma_200, 2) if ma_200 else None,
            'rsi': round(rsi_current, 2) if rsi_current else None,
            'volatility_30d': round(volatility_30d, 2) if volatility_30d else None,
            'volume_ratio': round(volume_ratio, 2) if volume_ratio else None,
            'high_52w': round(high_52w, 2),
            'low_52w': round(low_52w, 2),
            'dist_from_high': round(dist_from_high, 2) if dist_from_high else None,
            'dist_from_low': round(dist_from_low, 2) if dist_from_low else None,
        }
    except Exception as e:
        print(f"Error calculating indicators: {e}")
        return None

def screen_stocks(filters):
    """
    Screen stocks based on filters
    filters: dict with keys like min_price, max_price, min_pct_1m, max_rsi, etc.
    Returns list of stock symbols that match the criteria
    """
    available_stocks = get_available_stocks()
    matched_stocks = []
    
    for symbol in available_stocks:
        df = load_stock_data(symbol)
        if df is None:
            continue
        
        indicators = calculate_indicators(df)
        if indicators is None:
            continue
        
        # Apply filters
        match = True
        
        if 'min_price' in filters and filters['min_price']:
            if indicators['current_price'] < filters['min_price']:
                match = False
        
        if 'max_price' in filters and filters['max_price']:
            if indicators['current_price'] > filters['max_price']:
                match = False
        
        if 'min_pct_1d' in filters and filters['min_pct_1d']:
            if indicators['pct_1d'] < filters['min_pct_1d']:
                match = False
        
        if 'max_pct_1d' in filters and filters['max_pct_1d']:
            if indicators['pct_1d'] > filters['max_pct_1d']:
                match = False
        
        if 'min_pct_1m' in filters and filters['min_pct_1m']:
            if indicators['pct_1m'] < filters['min_pct_1m']:
                match = False
        
        if 'max_pct_1m' in filters and filters['max_pct_1m']:
            if indicators['pct_1m'] > filters['max_pct_1m']:
                match = False
        
        if 'min_pct_3m' in filters and filters['min_pct_3m']:
            if indicators['pct_3m'] < filters['min_pct_3m']:
                match = False
        
        if 'max_pct_3m' in filters and filters['max_pct_3m']:
            if indicators['pct_3m'] > filters['max_pct_3m']:
                match = False
        
        if 'min_rsi' in filters and filters['min_rsi']:
            if indicators['rsi'] is None or indicators['rsi'] < filters['min_rsi']:
                match = False
        
        if 'max_rsi' in filters and filters['max_rsi']:
            if indicators['rsi'] is None or indicators['rsi'] > filters['max_rsi']:
                match = False
        
        if 'min_volume_ratio' in filters and filters['min_volume_ratio']:
            if indicators['volume_ratio'] is None or indicators['volume_ratio'] < filters['min_volume_ratio']:
                match = False
        
        if 'above_ma_20' in filters and filters['above_ma_20']:
            if indicators['ma_20'] is None or indicators['current_price'] < indicators['ma_20']:
                match = False
        
        if 'above_ma_50' in filters and filters['above_ma_50']:
            if indicators['ma_50'] is None or indicators['current_price'] < indicators['ma_50']:
                match = False
        
        if 'above_ma_200' in filters and filters['above_ma_200']:
            if indicators['ma_200'] is None or indicators['current_price'] < indicators['ma_200']:
                match = False
        
        if match:
            matched_stocks.append({
                'symbol': symbol,
                'indicators': indicators
            })
    
    return matched_stocks
