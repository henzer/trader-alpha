import sys
from src.providers import YFinanceProvider
from src.models import Timeframe
from src.scoring import calculate_stock_score


def analyze_stocks(symbols: list[str], top_n: int = 10):
    print("=== Trader Alpha - Stock Scoring System ===\n")
    
    provider = YFinanceProvider(use_cache=True)
    
    print(f"Analyzing {len(symbols)} stocks...")
    print(f"Symbols: {', '.join(symbols)}\n")
    
    results = []
    
    for i, symbol in enumerate(symbols, 1):
        print(f"[{i}/{len(symbols)}] Processing {symbol}...", end=" ")
        
        try:
            df_weekly = provider.get_stock_data(symbol, Timeframe.WEEKLY, period="2y")
            df_monthly = provider.get_stock_data(symbol, Timeframe.MONTHLY, period="5y")
            
            score = calculate_stock_score(
                symbol=symbol,
                df_monthly=df_monthly,
                df_weekly=df_weekly
            )
            
            results.append(score)
            
            status = "✓" if score.score_breakdown.passed_filter else "✗"
            print(f"{status} Score: {score.score_breakdown.total_score}")
            
        except Exception as e:
            print(f"✗ Error: {str(e)}")
            continue
    
    results.sort(key=lambda x: x.score_breakdown.total_score, reverse=True)
    
    print("\n" + "="*80)
    print(f"TOP {min(top_n, len(results))} STOCKS BY SCORE")
    print("="*80)
    print(f"{'Rank':<6}{'Symbol':<10}{'Score':<8}{'Filter':<10}{'MB Score':<10}{'MB TF':<12}{'Fib Score':<10}{'Fib Zone':<15}")
    print("-"*80)
    
    for rank, stock in enumerate(results[:top_n], 1):
        sb = stock.score_breakdown
        mb_tf = sb.market_bias_timeframe.value if sb.market_bias_timeframe else "N/A"
        fib_zone = sb.fibonacci_zone.value if sb.fibonacci_zone else "N/A"
        filter_status = "PASS" if sb.passed_filter else "FAIL"
        
        print(f"{rank:<6}{stock.symbol:<10}{sb.total_score:<8}{filter_status:<10}"
              f"{sb.market_bias_score:<10}{mb_tf:<12}{sb.fibonacci_score:<10}{fib_zone:<15}")
    
    print("\n" + "="*80)
    print(f"Stocks passed filter: {sum(1 for s in results if s.score_breakdown.passed_filter)}/{len(results)}")
    print(f"Max possible score: 11 (6 Market Bias + 5 Fibonacci)")
    print("="*80)
    
    return results


if __name__ == "__main__":
    if len(sys.argv) > 1:
        symbols = sys.argv[1:]
    else:
        symbols = [
            "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA",
            "TSLA", "META", "AMD", "NFLX", "DIS"
        ]
    
    results = analyze_stocks(symbols, top_n=10)