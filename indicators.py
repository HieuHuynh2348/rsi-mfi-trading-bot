"""
Technical Indicators Module
Implements RSI and MFI calculations matching Pine Script logic
"""

import pandas as pd
import numpy as np


def validate_dataframe(df):
    """
    Validate and clean DataFrame for indicator calculations
    
    Args:
        df: pandas DataFrame with OHLCV data
    
    Returns:
        Cleaned DataFrame or None if invalid
    """
    if df is None or len(df) < 14:
        return None
    
    # Make a copy to avoid modifying original
    df = df.copy()
    
    # Ensure all required columns exist
    required_cols = ['high', 'low', 'close', 'volume']
    if not all(col in df.columns for col in required_cols):
        return None
    
    # Convert all columns to numeric, replacing errors with NaN
    for col in required_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Check for NaN values
    if df[required_cols].isnull().any().any():
        # Drop rows with NaN
        df = df.dropna(subset=required_cols)
        
        # Check if we still have enough data
        if len(df) < 14:
            return None
    
    return df


def calculate_hlcc4(df):
    """
    Calculate HLCC/4 price
    (High + Low + Close + Close) / 4
    
    Ensures numeric data types before calculation
    """
    # Ensure columns are numeric (convert strings to float)
    high = pd.to_numeric(df['high'], errors='coerce')
    low = pd.to_numeric(df['low'], errors='coerce')
    close = pd.to_numeric(df['close'], errors='coerce')
    
    return (high + low + close + close) / 4


def calculate_rsi(data, period=14):
    """
    Calculate RSI (Relative Strength Index) using HLCC/4
    Matches Pine Script custom RSI calculation
    
    Args:
        data: pandas Series or DataFrame column of price data (HLCC/4)
        period: RSI period (default 14)
    
    Returns:
        pandas Series of RSI values
    """
    # Convert to Series if needed and ensure numeric
    if isinstance(data, pd.DataFrame):
        # If it's a DataFrame, extract the first column
        data = data.iloc[:, 0]
    
    # Ensure it's a Series and numeric
    if not isinstance(data, pd.Series):
        data = pd.Series(data)
    
    data = pd.to_numeric(data, errors='coerce')
    
    # Drop NaN values
    data = data.dropna()
    
    if len(data) < period + 1:
        return pd.Series([np.nan] * len(data), index=data.index)
    
    delta = data.diff()
    
    # Separate gains and losses
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    
    # Calculate RMA (Rolling Moving Average, same as EMA with alpha=1/period)
    avg_gain = gain.ewm(alpha=1/period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/period, adjust=False).mean()
    
    # Calculate RS and RSI
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    # Handle division by zero
    rsi = rsi.fillna(100)
    
    return rsi


def calculate_mfi(df, period=14):
    """
    Calculate MFI (Money Flow Index)
    Matches Pine Script MFI calculation
    
    Args:
        df: pandas DataFrame with high, low, close, volume columns
        period: MFI period (default 14)
    
    Returns:
        pandas Series of MFI values
    """
    # Ensure all columns are numeric
    high = pd.to_numeric(df['high'], errors='coerce')
    low = pd.to_numeric(df['low'], errors='coerce')
    close = pd.to_numeric(df['close'], errors='coerce')
    volume = pd.to_numeric(df['volume'], errors='coerce')
    
    # Typical Price
    tp = (high + low + close) / 3
    
    # Money Flow
    mf = tp * volume
    
    # Positive and Negative Money Flow
    tp_change = tp.diff()
    positive_mf = mf.where(tp_change > 0, 0.0)
    negative_mf = mf.where(tp_change < 0, 0.0)
    
    # Sum over period
    positive_mf_sum = positive_mf.rolling(window=period).sum()
    negative_mf_sum = negative_mf.rolling(window=period).sum()
    
    # Money Flow Ratio
    mf_ratio = positive_mf_sum / negative_mf_sum
    
    # MFI calculation
    mfi = 100 - (100 / (1 + mf_ratio))
    
    # Handle division by zero
    mfi = mfi.fillna(100)
    
    return mfi


def get_signal(rsi_val, mfi_val, rsi_lower, rsi_upper, mfi_lower, mfi_upper):
    """
    Determine trading signal based on RSI and MFI consensus
    
    Returns:
        1 for BUY, -1 for SELL, 0 for NEUTRAL
    """
    # Individual signals
    rsi_signal = 1 if rsi_val < rsi_lower else (-1 if rsi_val > rsi_upper else 0)
    mfi_signal = 1 if mfi_val < mfi_lower else (-1 if mfi_val > mfi_upper else 0)
    
    # Consensus: both must agree
    if rsi_signal == 1 and mfi_signal == 1:
        return 1  # BUY
    elif rsi_signal == -1 and mfi_signal == -1:
        return -1  # SELL
    else:
        return 0  # NEUTRAL


def analyze_symbol(df, rsi_period, mfi_period, rsi_lower, rsi_upper, mfi_lower, mfi_upper):
    """
    Analyze a symbol's dataframe and return RSI, MFI, and signal
    
    Args:
        df: pandas DataFrame with OHLCV data
        rsi_period: RSI period
        mfi_period: MFI period
        rsi_lower: RSI lower threshold
        rsi_upper: RSI upper threshold
        mfi_lower: MFI lower threshold
        mfi_upper: MFI upper threshold
    
    Returns:
        dict with RSI, MFI, and signal values
    """
    try:
        # Validate and clean data first
        df = validate_dataframe(df)
        
        if df is None or len(df) < max(rsi_period, mfi_period) + 1:
            return None
        
        # Calculate HLCC/4
        hlcc4 = calculate_hlcc4(df)
        
        # Ensure hlcc4 is a valid Series
        if hlcc4 is None or not isinstance(hlcc4, pd.Series):
            return None
        
        # Calculate indicators
        rsi = calculate_rsi(hlcc4, rsi_period)
        mfi = calculate_mfi(df, mfi_period)
        
        # Check if calculations succeeded
        if rsi is None or mfi is None or len(rsi) == 0 or len(mfi) == 0:
            return None
        
        # Get latest values (current)
        latest_rsi = rsi.iloc[-1]
        latest_mfi = mfi.iloc[-1]
        
        # Check for NaN
        if pd.isna(latest_rsi) or pd.isna(latest_mfi):
            return None
        
        # Get previous values (last candle)
        last_rsi = rsi.iloc[-2] if len(rsi) >= 2 else latest_rsi
        last_mfi = mfi.iloc[-2] if len(mfi) >= 2 else latest_mfi
        
        # Calculate changes
        rsi_change = latest_rsi - last_rsi
        mfi_change = latest_mfi - last_mfi
        
        # Get signal
        signal = get_signal(latest_rsi, latest_mfi, rsi_lower, rsi_upper, mfi_lower, mfi_upper)
        
        return {
            'rsi': round(latest_rsi, 2),
            'mfi': round(latest_mfi, 2),
            'last_rsi': round(last_rsi, 2),
            'last_mfi': round(last_mfi, 2),
            'rsi_change': round(rsi_change, 2),
            'mfi_change': round(mfi_change, 2),
            'signal': signal,
            'rsi_series': rsi,
            'mfi_series': mfi
        }
    
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error in analyze_symbol: {e}")
        return None


def analyze_multi_timeframe(klines_dict, rsi_period, mfi_period, rsi_lower, rsi_upper, mfi_lower, mfi_upper):
    """
    Analyze multiple timeframes and return consensus
    
    Args:
        klines_dict: Dictionary of {timeframe: DataFrame}
        Other args: indicator parameters
    
    Returns:
        dict with analysis results for each timeframe and overall consensus
    """
    results = {}
    total_signal = 0
    
    for tf, df in klines_dict.items():
        analysis = analyze_symbol(df, rsi_period, mfi_period, rsi_lower, rsi_upper, mfi_lower, mfi_upper)
        if analysis:
            results[tf] = analysis
            total_signal += analysis['signal']
    
    # Overall consensus
    if total_signal > 0:
        consensus = "BUY"
    elif total_signal < 0:
        consensus = "SELL"
    else:
        consensus = "NEUTRAL"
    
    consensus_strength = abs(total_signal)
    
    return {
        'timeframes': results,
        'consensus': consensus,
        'consensus_strength': consensus_strength,
        'total_signal': total_signal
    }


def calculate_ohlc4(df):
    """
    Calculate OHLC/4 (smoother than close price)
    (Open + High + Low + Close) / 4
    
    Args:
        df: DataFrame with OHLC data
        
    Returns:
        Series with OHLC/4 values
    """
    # Ensure numeric types
    open_price = pd.to_numeric(df['open'], errors='coerce')
    high = pd.to_numeric(df['high'], errors='coerce')
    low = pd.to_numeric(df['low'], errors='coerce')
    close = pd.to_numeric(df['close'], errors='coerce')
    
    return (open_price + high + low + close) / 4


def calculate_stochastic(src, k_period=14, smooth=3):
    """
    Calculate Stochastic oscillator
    
    Args:
        src: Source data (price series)
        k_period: Lookback period for %K
        smooth: Smoothing period for %K
        
    Returns:
        Smoothed Stochastic %K values
    """
    # Calculate raw stochastic
    lowest_low = src.rolling(window=k_period).min()
    highest_high = src.rolling(window=k_period).max()
    
    # Avoid division by zero
    denominator = highest_high - lowest_low
    stoch = 100 * (src - lowest_low) / denominator.replace(0, np.nan)
    stoch = stoch.fillna(50)  # Fill NaN with neutral value
    
    # Smooth the stochastic
    smooth_stoch = stoch.rolling(window=smooth).mean()
    
    return smooth_stoch


def calculate_stochastic_d(stoch_k, d_period=3):
    """
    Calculate Stochastic %D (signal line)
    This is a moving average of %K
    
    Args:
        stoch_k: Stochastic %K series
        d_period: Smoothing period
        
    Returns:
        Stochastic %D values
    """
    return stoch_k.rolling(window=d_period).mean()


def calculate_rsi_rma(src, length=14):
    """
    Calculate RSI using RMA (same as Pine Script ta.rma)
    This is the exact implementation from TradingView
    
    Args:
        src: Source data series
        length: RSI period
        
    Returns:
        RSI values
    """
    # Calculate price changes
    delta = src.diff()
    
    # Separate gains and losses
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    
    # Calculate RMA (Exponential Moving Average with alpha=1/length)
    # This matches Pine Script's ta.rma() exactly
    alpha = 1.0 / length
    avg_gain = gain.ewm(alpha=alpha, adjust=False).mean()
    avg_loss = loss.ewm(alpha=alpha, adjust=False).mean()
    
    # Calculate RS and RSI
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    # Handle division by zero (when avg_loss is 0, RSI = 100)
    rsi = rsi.fillna(100)
    
    return rsi


def analyze_stoch_rsi(df, stoch_k_period=14, stoch_smooth=3, stoch_d_period=3,
                      rsi_length=14, stoch_lower=20, stoch_upper=80, 
                      rsi_lower=30, rsi_upper=70):
    """
    Analyze Stochastic + RSI on OHLC/4 data
    This matches the Pine Script Stoch+RSI Multi-TF logic
    
    Args:
        df: DataFrame with OHLC data
        stoch_k_period: Stochastic %K period
        stoch_smooth: Smoothing for %K
        stoch_d_period: %D period (signal line)
        rsi_length: RSI period
        stoch_lower: Stochastic oversold level
        stoch_upper: Stochastic overbought level
        rsi_lower: RSI oversold level
        rsi_upper: RSI overbought level
        
    Returns:
        Dict with Stochastic, RSI, and signal
    """
    try:
        # Validate DataFrame
        df = validate_dataframe(df)
        if df is None:
            return None
        
        # Calculate OHLC/4 (smoother than close)
        ohlc4 = calculate_ohlc4(df)
        
        # Calculate RSI on OHLC/4 using RMA
        rsi = calculate_rsi_rma(ohlc4, rsi_length)
        
        # Calculate Stochastic on OHLC/4
        stoch_k = calculate_stochastic(ohlc4, stoch_k_period, stoch_smooth)
        stoch_d = calculate_stochastic_d(stoch_k, stoch_d_period)
        
        # Get latest values
        latest_rsi = float(rsi.iloc[-1])
        latest_stoch_k = float(stoch_k.iloc[-1])
        latest_stoch_d = float(stoch_d.iloc[-1])
        
        # Determine signals
        rsi_signal = 0
        if latest_rsi < rsi_lower:
            rsi_signal = 1  # Oversold - BUY
        elif latest_rsi > rsi_upper:
            rsi_signal = -1  # Overbought - SELL
        
        stoch_signal = 0
        if latest_stoch_k < stoch_lower:
            stoch_signal = 1  # Oversold - BUY
        elif latest_stoch_k > stoch_upper:
            stoch_signal = -1  # Overbought - SELL
        
        # Consensus signal (both must agree)
        if rsi_signal == 1 and stoch_signal == 1:
            final_signal = 1  # BUY
        elif rsi_signal == -1 and stoch_signal == -1:
            final_signal = -1  # SELL
        else:
            final_signal = 0  # NEUTRAL
        
        return {
            'rsi': round(latest_rsi, 2),
            'stoch_k': round(latest_stoch_k, 2),
            'stoch_d': round(latest_stoch_d, 2),
            'rsi_signal': rsi_signal,
            'stoch_signal': stoch_signal,
            'signal': final_signal,
            'signal_text': 'BUY' if final_signal == 1 else 'SELL' if final_signal == -1 else 'NEUTRAL',
            'rsi_series': rsi,
            'stoch_k_series': stoch_k,
            'stoch_d_series': stoch_d
        }
        
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error in analyze_stoch_rsi: {e}")
        return None

