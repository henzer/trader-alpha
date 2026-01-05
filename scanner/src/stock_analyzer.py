from src.providers import YFinanceProvider
from src.models import Timeframe
from src.scoring import calculate_stock_score
from src.indicators import calculate_fibonacci_retracement
from typing import Optional, Dict
import pandas as pd

class StockAnalyzer:
    def __init__(self, use_cache: bool = False):
        self.provider = YFinanceProvider(use_cache=use_cache)
    
    def analyze(self, symbol: str, preloaded_data: Optional[Dict[str, pd.DataFrame]] = None) -> Optional[Dict]:
        try:
            if preloaded_data:
                df_daily = preloaded_data.get('daily')
                df_weekly = preloaded_data.get('weekly')
                df_monthly = preloaded_data.get('monthly')
            else:
                df_daily = self.provider.get_stock_data(symbol, Timeframe.DAILY, period="2y")
                df_weekly = self.provider.get_stock_data(symbol, Timeframe.WEEKLY, period="2y")
                df_monthly = self.provider.get_stock_data(symbol, Timeframe.MONTHLY, period="2y")
            
            if df_daily is None or df_weekly is None or df_monthly is None:
                print(f"❌ {symbol}: No data available")
                return None
            
            if df_daily.empty or df_weekly.empty or df_monthly.empty:
                print(f"❌ {symbol}: Empty dataframes")
                return None
            
            score = calculate_stock_score(symbol, df_monthly, df_weekly, df_daily)
            
            fib_result = calculate_fibonacci_retracement(df_daily, lookback=50)
            
            current_price = float(df_daily['close'].iloc[-1]) if not df_daily.empty else None
            
            result = {
                "total_score": score.score_breakdown.total_score,
                "passed_filter": score.score_breakdown.passed_filter,
                "market_bias_score": score.score_breakdown.market_bias_score,
                "market_bias_timeframe": score.score_breakdown.market_bias_timeframe.value if score.score_breakdown.market_bias_timeframe else None,
                "fibonacci_score": score.score_breakdown.fibonacci_score,
                "fibonacci_zone": score.score_breakdown.fibonacci_zone.value if score.score_breakdown.fibonacci_zone else None,
                "bx_trender_color": score.score_breakdown.bx_trender_color.value if score.score_breakdown.bx_trender_color else None,
                "swing_high": float(fib_result.swing_high) if fib_result else None,
                "swing_low": float(fib_result.swing_low) if fib_result else None,
                "current_price": current_price,
            }
            
            print(f"✅ {symbol}: Score={result['total_score']}/11, Filter={'PASS' if result['passed_filter'] else 'FAIL'}")
            
            return result
            
        except Exception as e:
            print(f"❌ {symbol}: Error - {str(e)}")
            return None