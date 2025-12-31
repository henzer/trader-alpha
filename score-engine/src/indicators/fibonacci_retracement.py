import pandas as pd
import numpy as np
from typing import Tuple, Optional
from ..types import FibonacciResult, FibonacciZone


def find_pivot_high(df: pd.DataFrame, lookback: int = 5) -> Tuple[Optional[int], Optional[float]]:
    highs = df['high'].values
    
    for i in range(len(highs) - lookback - 1, lookback - 1, -1):
        is_pivot = True
        current_high = highs[i]
        
        for j in range(1, lookback + 1):
            if i - j < 0 or i + j >= len(highs):
                is_pivot = False
                break
            if highs[i - j] >= current_high or highs[i + j] >= current_high:
                is_pivot = False
                break
        
        if is_pivot:
            return i, current_high
    
    return None, None


def find_pivot_low(df: pd.DataFrame, lookback: int = 5) -> Tuple[Optional[int], Optional[float]]:
    lows = df['low'].values
    
    for i in range(len(lows) - lookback - 1, lookback - 1, -1):
        is_pivot = True
        current_low = lows[i]
        
        for j in range(1, lookback + 1):
            if i - j < 0 or i + j >= len(lows):
                is_pivot = False
                break
            if lows[i - j] <= current_low or lows[i + j] <= current_low:
                is_pivot = False
                break
        
        if is_pivot:
            return i, current_low
    
    return None, None


def calculate_fibonacci_levels(swing_high: float, swing_low: float) -> dict:
    diff = swing_high - swing_low
    
    return {
        '0': swing_high,
        '0.236': swing_high - (diff * 0.236),
        '0.382': swing_high - (diff * 0.382),
        '0.5': swing_high - (diff * 0.5),
        '0.618': swing_high - (diff * 0.618),
        '0.786': swing_high - (diff * 0.786),
        '0.826': swing_high - (diff * 0.826),
        '1': swing_low
    }


def get_fibonacci_zone(price: float, fib_levels: dict) -> FibonacciZone:
    fib_618 = fib_levels['0.618']
    fib_786 = fib_levels['0.786']
    fib_826 = fib_levels['0.826']
    
    if fib_826 <= price <= fib_786:
        return FibonacciZone.GOLDEN_ZONE
    elif fib_786 < price <= fib_618:
        return FibonacciZone.SMART_MONEY_ZONE
    else:
        return FibonacciZone.OUTSIDE


def calculate_fibonacci_retracement(
    df: pd.DataFrame,
    lookback: int = 10
) -> Optional[FibonacciResult]:
    pivot_high_idx, swing_high = find_pivot_high(df, lookback)
    pivot_low_idx, swing_low = find_pivot_low(df, lookback)
    
    if swing_high is None or swing_low is None:
        return None
    
    if pivot_high_idx < pivot_low_idx:
        return None
    
    fib_levels = calculate_fibonacci_levels(swing_high, swing_low)
    
    current_price = df['close'].iloc[-1]
    
    zone = get_fibonacci_zone(current_price, fib_levels)
    
    return FibonacciResult(
        swing_high=float(swing_high),
        swing_low=float(swing_low),
        current_price=float(current_price),
        fib_0618=float(fib_levels['0.618']),
        fib_0786=float(fib_levels['0.786']),
        fib_0826=float(fib_levels['0.826']),
        zone=zone,
        in_smart_money_zone=zone in [FibonacciZone.GOLDEN_ZONE, FibonacciZone.SMART_MONEY_ZONE]
    )
