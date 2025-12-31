#!/usr/bin/env python3
import sys
import os
from pathlib import Path
from datetime import date
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Optional
import time

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "data-provider"))

from list_fetcher import get_all_symbols, get_symbol_to_lists_mapping
from stock_analyzer import StockAnalyzer
from supabase_client import SupabaseClient
from src.providers import YFinanceProvider
from src.models import Timeframe

def analyze_single_stock(symbol: str, analyzer: StockAnalyzer, all_data: Dict, symbol_to_lists: Dict) -> Optional[tuple]:
    preloaded = {
        'daily': all_data['daily'].get(symbol),
        'weekly': all_data['weekly'].get(symbol),
        'monthly': all_data['monthly'].get(symbol)
    }
    
    if any(v is None for v in preloaded.values()):
        return None
    
    result = analyzer.analyze(symbol, preloaded_data=preloaded)
    if result:
        result['list_names'] = symbol_to_lists.get(symbol, [])
        return (symbol, result)
    return None

def main():
    print(f"{'='*60}")
    print(f"  Daily Stock Scanner - {date.today()}")
    print(f"{'='*60}\n")
    
    print("1. Fetching symbols from lists...")
    symbols = get_all_symbols()
    symbol_to_lists = get_symbol_to_lists_mapping()
    
    print(f"   Found {len(symbols)} unique symbols\n")
    
    print("2. Downloading market data in batches...")
    provider = YFinanceProvider(use_cache=False)
    
    start_time = time.time()
    
    print("   📥 Downloading DAILY data...")
    daily_data = provider.get_multiple_stocks(symbols, Timeframe.DAILY, period="2y")
    print(f"      ✅ {len(daily_data)}/{len(symbols)} symbols downloaded")
    
    print("   📥 Downloading WEEKLY data...")
    weekly_data = provider.get_multiple_stocks(symbols, Timeframe.WEEKLY, period="2y")
    print(f"      ✅ {len(weekly_data)}/{len(symbols)} symbols downloaded")
    
    print("   📥 Downloading MONTHLY data...")
    monthly_data = provider.get_multiple_stocks(symbols, Timeframe.MONTHLY, period="2y")
    print(f"      ✅ {len(monthly_data)}/{len(symbols)} symbols downloaded")
    
    download_time = time.time() - start_time
    print(f"\n   ⏱️  Download completed in {download_time:.1f} seconds\n")
    
    valid_symbols = set(daily_data.keys()) & set(weekly_data.keys()) & set(monthly_data.keys())
    print(f"3. Analyzing {len(valid_symbols)} stocks with complete data...")
    
    all_data = {
        'daily': daily_data,
        'weekly': weekly_data,
        'monthly': monthly_data
    }
    
    analyzer = StockAnalyzer(use_cache=False)
    results: Dict[str, Dict] = {}
    
    analysis_start = time.time()
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(analyze_single_stock, symbol, analyzer, all_data, symbol_to_lists): symbol 
                   for symbol in valid_symbols}
        
        completed = 0
        total = len(valid_symbols)
        
        for future in as_completed(futures):
            completed += 1
            result = future.result()
            
            if result:
                symbol, data = result
                results[symbol] = data
            
            if completed % 25 == 0:
                print(f"   Progress: {completed}/{total} ({completed*100//total}%)")
    
    analysis_time = time.time() - analysis_start
    print(f"\n   ✅ Analysis complete: {len(results)}/{total} successful")
    print(f"   ⏱️  Analysis completed in {analysis_time:.1f} seconds\n")
    
    print("4. Saving to Supabase...")
    supabase = SupabaseClient()
    
    save_start = time.time()
    
    saved = supabase.save_stock_scores_batch(results)
    print(f"   ✅ Saved {saved}/{len(results)} stocks to database in 1 batch request")
    
    save_time = time.time() - save_start
    print(f"   ⏱️  Save completed in {save_time:.1f} seconds\n")
    
    print("5. Top 10 stocks by score:")
    sorted_stocks = sorted(results.items(), key=lambda x: x[1]['total_score'], reverse=True)
    for i, (symbol, data) in enumerate(sorted_stocks[:10], 1):
        filter_status = "PASS" if data['passed_filter'] else "FAIL"
        mb_tf = data['market_bias_timeframe'] or 'N/A'
        fib_zone = data['fibonacci_zone'] or 'N/A'
        print(f"   {i:2d}. {symbol:6s} - {data['total_score']:2d}/11 ({filter_status}) | MB: {mb_tf} | Fib: {fib_zone}")
    
    total_time = time.time() - start_time
    
    print(f"\n{'='*60}")
    print(f"  Scan complete!")
    print(f"  Total time: {total_time:.1f} seconds ({total_time/60:.1f} minutes)")
    print(f"  Download: {download_time:.1f}s | Analysis: {analysis_time:.1f}s | Save: {save_time:.1f}s")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()