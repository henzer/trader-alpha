import pandas as pd
from typing import Tuple, Optional
from ..indicators import check_market_bias
from ..types import Timeframe


def score_market_bias(
    df_weekly: pd.DataFrame,
    df_monthly: pd.DataFrame,
    ha_len: int = 20,
    ha_len2: int = 7
) -> Tuple[int, Optional[Timeframe]]:
    monthly_result = check_market_bias(df_monthly, Timeframe.MONTHLY, ha_len, ha_len2)
    
    if monthly_result.in_range:
        return 6, Timeframe.MONTHLY
    
    weekly_result = check_market_bias(df_weekly, Timeframe.WEEKLY, ha_len, ha_len2)
    
    if weekly_result.in_range:
        return 3, Timeframe.WEEKLY
    
    return 0, None