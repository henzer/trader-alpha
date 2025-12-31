import pandas as pd
from ..indicators import get_latest_bx_trender
from ..types import BXTrenderColor


def passes_macro_uptrend_filter(df_monthly: pd.DataFrame) -> bool:
    result = get_latest_bx_trender(df_monthly, use_short=True)
    
    return result.color != BXTrenderColor.DARK_RED