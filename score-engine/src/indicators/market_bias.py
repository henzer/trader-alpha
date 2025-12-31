import pandas as pd
import numpy as np
from typing import Tuple
from ..types import MarketBiasResult, Timeframe


def calculate_ema(series: pd.Series, period: int) -> pd.Series:
    return series.ewm(span=period, adjust=False).mean()


def calculate_heikin_ashi(df: pd.DataFrame, ha_len: int = 20) -> pd.DataFrame:
    o = calculate_ema(df['open'], ha_len)
    c = calculate_ema(df['close'], ha_len)
    h = calculate_ema(df['high'], ha_len)
    l = calculate_ema(df['low'], ha_len)
    
    haclose = (o + h + l + c) / 4
    
    xhaopen = (o + c) / 2
    haopen = pd.Series(index=df.index, dtype=float)
    haopen.iloc[0] = xhaopen.iloc[0]
    
    for i in range(1, len(df)):
        haopen.iloc[i] = (haopen.iloc[i-1] + haclose.iloc[i-1]) / 2
    
    hahigh = pd.concat([h, haopen, haclose], axis=1).max(axis=1)
    halow = pd.concat([l, haopen, haclose], axis=1).min(axis=1)
    
    return pd.DataFrame({
        'open': haopen,
        'close': haclose,
        'high': hahigh,
        'low': halow
    })


def calculate_market_bias(
    df: pd.DataFrame,
    ha_len: int = 20,
    ha_len2: int = 7
) -> Tuple[pd.Series, pd.Series]:
    ha_df = calculate_heikin_ashi(df, ha_len)
    
    o2 = calculate_ema(ha_df['open'], ha_len2)
    c2 = calculate_ema(ha_df['close'], ha_len2)
    h2 = calculate_ema(ha_df['high'], ha_len2)
    l2 = calculate_ema(ha_df['low'], ha_len2)
    
    return h2, l2


def check_market_bias(
    df: pd.DataFrame,
    timeframe: Timeframe,
    ha_len: int = 20,
    ha_len2: int = 7
) -> MarketBiasResult:
    h2, l2 = calculate_market_bias(df, ha_len, ha_len2)
    
    current_price = df['close'].iloc[-1]
    bias_high = h2.iloc[-1]
    bias_low = l2.iloc[-1]
    
    in_range = bias_low <= current_price <= bias_high
    
    return MarketBiasResult(
        timeframe=timeframe.value,
        in_range=in_range,
        price=float(current_price),
        bias_low=float(bias_low),
        bias_high=float(bias_high)
    )