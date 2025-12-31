import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "data-provider"))

from src import YFinanceProvider, Timeframe


def test_data_provider():
    print("=== Testing Data Provider ===\n")
    
    provider = YFinanceProvider(use_cache=True)
    
    symbol = "AAPL"
    print(f"Fetching data for {symbol}...\n")
    
    print("1. Weekly data (2y period):")
    df_weekly = provider.get_stock_data(symbol, Timeframe.WEEKLY, period="2y")
    print(f"   Shape: {df_weekly.shape}")
    print(f"   Columns: {df_weekly.columns.tolist()}")
    print(f"   Date range: {df_weekly.index[0]} to {df_weekly.index[-1]}")
    print(f"\n   First 3 rows:")
    print(df_weekly.head(3))
    print(f"\n   Last 3 rows:")
    print(df_weekly.tail(3))
    
    print("\n\n2. Monthly data (5y period):")
    df_monthly = provider.get_stock_data(symbol, Timeframe.MONTHLY, period="5y")
    print(f"   Shape: {df_monthly.shape}")
    print(f"   Columns: {df_monthly.columns.tolist()}")
    print(f"   Date range: {df_monthly.index[0]} to {df_monthly.index[-1]}")
    print(f"\n   First 3 rows:")
    print(df_monthly.head(3))
    
    print("\n\n3. Testing cache (should be faster):")
    import time
    start = time.time()
    df_weekly_cached = provider.get_stock_data(symbol, Timeframe.WEEKLY, period="2y")
    elapsed = time.time() - start
    print(f"   Fetched in {elapsed:.4f} seconds")
    print(f"   Data from cache? {df_weekly.equals(df_weekly_cached)}")
    
    print("\n\n4. Testing multiple stocks:")
    symbols = ["AAPL", "MSFT", "GOOGL"]
    data = provider.get_multiple_stocks(symbols, Timeframe.WEEKLY, period="1y")
    print(f"   Fetched {len(data)} stocks")
    for sym, df in data.items():
        print(f"   {sym}: {df.shape[0]} rows")
    
    print("\n=== Test Complete ===")


if __name__ == "__main__":
    test_data_provider()