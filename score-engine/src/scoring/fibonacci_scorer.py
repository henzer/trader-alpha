import pandas as pd
from typing import Tuple, Optional
from ..indicators import calculate_fibonacci_retracement
from ..types import FibonacciZone, FibonacciResult


def score_fibonacci(
    df: pd.DataFrame,
    lookback: int = 10
) -> Tuple[int, Optional[FibonacciZone], Optional[FibonacciResult]]:
    fib_result = calculate_fibonacci_retracement(df, lookback)
    
    if fib_result is None:
        return 0, None, None
    
    if fib_result.zone == FibonacciZone.GOLDEN_ZONE:
        return 5, FibonacciZone.GOLDEN_ZONE, fib_result
    elif fib_result.zone == FibonacciZone.SMART_MONEY_ZONE:
        return 3, FibonacciZone.SMART_MONEY_ZONE, fib_result
    else:
        return 0, FibonacciZone.OUTSIDE, fib_result