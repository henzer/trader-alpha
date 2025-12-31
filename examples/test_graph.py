import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "data-provider"))
sys.path.insert(0, str(Path(__file__).parent.parent / "score-engine"))
sys.path.insert(0, str(Path(__file__).parent.parent / "graph"))

from src.providers import YFinanceProvider
from src.models import Timeframe
from src.indicators import calculate_bx_trender, calculate_market_bias, calculate_fibonacci_retracement
from src.scoring import calculate_stock_score
from src import StockChart


def test_stock_chart(symbol: str = "NFLX"):
    print(f"=== Testing Graph Module with {symbol} ===\n")
    
    provider = YFinanceProvider(use_cache=True)
    
    print("1. Fetching data (2y for warm-up, showing 1y)...")
    df_daily_full = provider.get_stock_data(symbol, Timeframe.DAILY, period="2y")
    df_weekly_full = provider.get_stock_data(symbol, Timeframe.WEEKLY, period="2y")
    df_monthly_full = provider.get_stock_data(symbol, Timeframe.MONTHLY, period="2y")
    
    df_daily = df_daily_full.tail(252)
    df_weekly = df_weekly_full.tail(52)
    df_monthly = df_monthly_full.tail(12)
    
    print(f"   Daily data: {df_daily.shape[0]} rows (from {df_daily_full.shape[0]} total)")
    print(f"   Weekly data: {df_weekly.shape[0]} rows (from {df_weekly_full.shape[0]} total)")
    print(f"   Monthly data: {df_monthly.shape[0]} rows (from {df_monthly_full.shape[0]} total)")
    
    print("\n2. Calculating score...")
    score = calculate_stock_score(symbol, df_monthly_full, df_weekly_full, df_daily_full)
    print(f"   Total Score: {score.score_breakdown.total_score}/11")
    print(f"   Passed Filter: {score.score_breakdown.passed_filter}")
    print(f"   Market Bias: {score.score_breakdown.market_bias_score} pts")
    print(f"   Fibonacci: {score.score_breakdown.fibonacci_score} pts")
    
    print("\n3. Calculating indicators for chart...")
    
    bx_monthly_full = calculate_bx_trender(df_monthly_full, use_short=True, apply_t3=False)
    bx_weekly_full = calculate_bx_trender(df_weekly_full, use_short=True, apply_t3=False)
    bx_monthly = bx_monthly_full.tail(12)
    bx_weekly = bx_weekly_full.tail(52)
    print(f"   BX-Trender calculated for monthly and weekly")
    
    bias_high_weekly_full, bias_low_weekly_full = calculate_market_bias(df_weekly_full, ha_len=20, ha_len2=7)
    bias_high_weekly = bias_high_weekly_full.tail(52)
    bias_low_weekly = bias_low_weekly_full.tail(52)
    print(f"   Market Bias calculated (weekly)")
    
    bias_high_monthly_full, bias_low_monthly_full = calculate_market_bias(df_monthly_full, ha_len=20, ha_len2=7)
    bias_high_monthly = bias_high_monthly_full.tail(12)
    bias_low_monthly = bias_low_monthly_full.tail(12)
    print(f"   Market Bias calculated (monthly)")
    
    fib_result = calculate_fibonacci_retracement(df_daily, lookback=50)
    if fib_result:
        print(f"   Fibonacci: Swing High={fib_result.swing_high:.2f}, Swing Low={fib_result.swing_low:.2f}")
        print(f"   Current Zone: {fib_result.zone.value}")
    
    print("\n4. Creating chart...")
    chart = StockChart(symbol=symbol, df=df_daily)
    
    score_data = {
        'total_score': score.score_breakdown.total_score,
        'passed_filter': score.score_breakdown.passed_filter,
        'market_bias_score': score.score_breakdown.market_bias_score,
        'market_bias_timeframe': score.score_breakdown.market_bias_timeframe.value if score.score_breakdown.market_bias_timeframe else 'N/A',
        'fibonacci_score': score.score_breakdown.fibonacci_score,
        'fibonacci_zone': score.score_breakdown.fibonacci_zone.value if score.score_breakdown.fibonacci_zone else 'N/A',
        'bx_trender_color': score.score_breakdown.bx_trender_color.value if score.score_breakdown.bx_trender_color else 'N/A'
    }
    
    chart.set_score_data(score_data)
    chart.create_base_chart(with_bx_trender=True, bx_rows=2)
    
    chart.add_market_bias(bias_high_weekly, bias_low_weekly, name="Weekly Market Bias", df_index=df_weekly.index, resample_to_daily=True)
    chart.add_market_bias(bias_high_monthly, bias_low_monthly, name="Monthly Market Bias", df_index=df_monthly.index, resample_to_daily=True, color='blue')
    
    if fib_result:
        chart.add_fibonacci(
            swing_high=fib_result.swing_high,
            swing_low=fib_result.swing_low,
            show_all_levels=False
        )
    
    chart.add_bx_trender(bx_monthly, row=2, name='Monthly BX-Trender', df_index=df_monthly.index, resample_to_daily=True)
    chart.add_bx_trender(bx_weekly, row=3, name='Weekly BX-Trender', df_index=df_weekly.index, resample_to_daily=True)
    
    chart.add_score_annotation()
    
    print("\n5. Saving chart...")
    output_path = chart.save()
    print(f"   Chart saved to: {output_path}")
    
    print("\n=== Test Complete ===")
    print(f"\nOpen the chart in your browser:")
    print(f"open {output_path}")
    
    return output_path


if __name__ == "__main__":
    import sys
    symbol = sys.argv[1] if len(sys.argv) > 1 else "NFLX"
    test_stock_chart(symbol)
