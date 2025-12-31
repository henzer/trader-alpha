import sys
from src.providers import YFinanceProvider
from src.models import Timeframe
from src.scoring import calculate_stock_score


def analyze_stocks(symbols: list[str]):
    print(f"=== Analyzing {len(symbols)} stocks ===\n")
    
    provider = YFinanceProvider(use_cache=True)
    results = []
    
    for i, symbol in enumerate(symbols, 1):
        print(f"[{i}/{len(symbols)}] Analyzing {symbol}...", end=" ")
        
        try:
            df_monthly = provider.get_stock_data(symbol, Timeframe.MONTHLY, period="2y")
            df_weekly = provider.get_stock_data(symbol, Timeframe.WEEKLY, period="2y")
            
            score = calculate_stock_score(symbol, df_monthly, df_weekly)
            
            results.append({
                'symbol': symbol,
                'total_score': score.score_breakdown.total_score,
                'passed_filter': score.score_breakdown.passed_filter,
                'market_bias_score': score.score_breakdown.market_bias_score,
                'market_bias_tf': score.score_breakdown.market_bias_timeframe.value if score.score_breakdown.market_bias_timeframe else 'N/A',
                'fibonacci_score': score.score_breakdown.fibonacci_score,
                'fibonacci_zone': score.score_breakdown.fibonacci_zone.value if score.score_breakdown.fibonacci_zone else 'N/A',
                'bx_color': score.score_breakdown.bx_trender_color.value if score.score_breakdown.bx_trender_color else 'N/A'
            })
            
            print(f"Score: {score.score_breakdown.total_score}/11 - Filter: {'PASS' if score.score_breakdown.passed_filter else 'FAIL'}")
        
        except Exception as e:
            print(f"ERROR: {str(e)}")
            results.append({
                'symbol': symbol,
                'total_score': 0,
                'passed_filter': False,
                'error': str(e)
            })
    
    results.sort(key=lambda x: x['total_score'], reverse=True)
    
    print("\n" + "="*80)
    print("TOP STOCKS BY SCORE")
    print("="*80)
    print(f"{'Rank':<6} {'Symbol':<8} {'Score':<8} {'Filter':<8} {'MB':<6} {'Fib':<6} {'BX-Color':<12} {'Fib Zone':<20}")
    print("-"*80)
    
    for i, result in enumerate(results, 1):
        if 'error' in result:
            print(f"{i:<6} {result['symbol']:<8} ERROR: {result['error']}")
        else:
            filter_status = "PASS ✅" if result['passed_filter'] else "FAIL ❌"
            print(f"{i:<6} {result['symbol']:<8} {result['total_score']:<8} {filter_status:<8} "
                  f"{result['market_bias_score']:<6} {result['fibonacci_score']:<6} "
                  f"{result['bx_color']:<12} {result['fibonacci_zone']:<20}")
    
    print("\n" + "="*80)
    print("STOCKS THAT PASSED FILTER (sorted by score)")
    print("="*80)
    
    passed_stocks = [r for r in results if r.get('passed_filter', False)]
    
    if passed_stocks:
        for i, result in enumerate(passed_stocks, 1):
            print(f"{i}. {result['symbol']}: {result['total_score']}/11 pts "
                  f"(MB: {result['market_bias_score']} [{result['market_bias_tf']}], "
                  f"Fib: {result['fibonacci_score']} [{result['fibonacci_zone']}])")
    else:
        print("No stocks passed the macro uptrend filter")
    
    return results


if __name__ == "__main__":
    # Top 20 most traded stocks
    symbols = [
        "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA",
        "META", "TSLA", "BRK.B", "JPM", "V",
        "UNH", "WMT", "XOM", "MA", "PG",
        "JNJ", "COST", "HD", "NFLX", "DIS"
    ]
    
    analyze_stocks(symbols)
