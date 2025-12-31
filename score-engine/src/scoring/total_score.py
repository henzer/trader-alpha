import pandas as pd
from ..filters import passes_macro_uptrend_filter
from ..indicators import get_latest_bx_trender
from ..types import StockScore, ScoreBreakdown
from .market_bias_scorer import score_market_bias
from .fibonacci_scorer import score_fibonacci


def calculate_stock_score(
    symbol: str,
    df_monthly: pd.DataFrame,
    df_weekly: pd.DataFrame,
    df_daily: pd.DataFrame = None,
    ha_len: int = 20,
    ha_len2: int = 7,
    fib_lookback: int = 50
) -> StockScore:
    passed_filter = passes_macro_uptrend_filter(df_monthly)
    
    market_bias_score, market_bias_tf = score_market_bias(
        df_weekly, df_monthly, ha_len, ha_len2
    )
    
    fib_df = df_daily if df_daily is not None else df_weekly
    fibonacci_score, fibonacci_zone, _ = score_fibonacci(
        fib_df, fib_lookback
    )
    
    total_score = market_bias_score + fibonacci_score
    
    bx_result = get_latest_bx_trender(df_monthly, use_short=True)
    
    return StockScore(
        symbol=symbol,
        score_breakdown=ScoreBreakdown(
            market_bias_score=market_bias_score,
            market_bias_timeframe=market_bias_tf,
            fibonacci_score=fibonacci_score,
            fibonacci_zone=fibonacci_zone,
            total_score=total_score,
            passed_filter=passed_filter,
            bx_trender_color=bx_result.color
        )
    )