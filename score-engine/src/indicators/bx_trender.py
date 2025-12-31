import pandas as pd
import numpy as np
from typing import Tuple
from ..types import BXTrenderColor, BXTrenderResult


def calculate_rsi(series: pd.Series, period: int) -> pd.Series:
    delta = series.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    
    alpha = 1.0 / period
    avg_gain = gain.ewm(alpha=alpha, adjust=False).mean()
    avg_loss = loss.ewm(alpha=alpha, adjust=False).mean()
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def calculate_ema(series: pd.Series, period: int) -> pd.Series:
    return series.ewm(span=period, adjust=False).mean()


def calculate_t3(series: pd.Series, period: int) -> pd.Series:
    b = 0.7
    c1 = -b**3
    c2 = 3*b**2 + 3*b**3
    c3 = -6*b**2 - 3*b - 3*b**3
    c4 = 1 + 3*b + b**3 + 3*b**2
    
    xe1 = calculate_ema(series, period)
    xe2 = calculate_ema(xe1, period)
    xe3 = calculate_ema(xe2, period)
    xe4 = calculate_ema(xe3, period)
    xe5 = calculate_ema(xe4, period)
    xe6 = calculate_ema(xe5, period)
    
    t3 = c1 * xe6 + c2 * xe5 + c3 * xe4 + c4 * xe3
    return t3


def calculate_bx_trender(
    df: pd.DataFrame,
    short_l1: int = 5,
    short_l2: int = 20,
    short_l3: int = 15,
    long_l1: int = 20,
    long_l2: int = 15,
    use_short: bool = True,
    apply_t3: bool = False
) -> pd.Series:
    close = df['close']
    
    if use_short:
        ema_diff = calculate_ema(close, short_l1) - calculate_ema(close, short_l2)
        xtrender = calculate_rsi(ema_diff, short_l3) - 50
        if apply_t3:
            xtrender_smoothed = calculate_t3(xtrender, 5)
            return xtrender_smoothed
        return xtrender
    else:
        ema_close = calculate_ema(close, long_l1)
        xtrender = calculate_rsi(ema_close, long_l2) - 50
        return xtrender


def get_bx_trender_color(value: float, prev_value: float) -> BXTrenderColor:
    is_positive = value > 0
    is_rising = value > prev_value
    
    if is_positive and is_rising:
        return BXTrenderColor.LIME
    elif is_positive and not is_rising:
        return BXTrenderColor.DARK_GREEN
    elif not is_positive and is_rising:
        return BXTrenderColor.RED
    else:
        return BXTrenderColor.DARK_RED


def get_latest_bx_trender(
    df: pd.DataFrame,
    short_l1: int = 5,
    short_l2: int = 20,
    short_l3: int = 15,
    long_l1: int = 20,
    long_l2: int = 15,
    use_short: bool = True
) -> BXTrenderResult:
    xtrender_series = calculate_bx_trender(
        df, short_l1, short_l2, short_l3, long_l1, long_l2, use_short
    )
    
    latest_value = xtrender_series.iloc[-1]
    prev_value = xtrender_series.iloc[-2]
    
    color = get_bx_trender_color(latest_value, prev_value)
    is_uptrend = color != BXTrenderColor.DARK_RED
    
    return BXTrenderResult(
        value=float(latest_value),
        color=color,
        is_uptrend=is_uptrend
    )