#!/usr/bin/env python3
import sys
from pathlib import Path
from datetime import date

sys.path.insert(0, str(Path(__file__).parent / "src"))

from supabase_client import SupabaseClient

def test_connection():
    print("=" * 60)
    print("  Testing Supabase Connection")
    print("=" * 60)
    
    try:
        print("\n1. Initializing Supabase client...")
        client = SupabaseClient()
        print("   ✅ Client initialized successfully")
        
        print("\n2. Testing insert...")
        test_data = {
            "total_score": 11,
            "passed_filter": True,
            "market_bias_score": 6,
            "market_bias_timeframe": "1mo",
            "fibonacci_score": 5,
            "fibonacci_zone": "golden_zone",
            "bx_trender_color": "green",
            "swing_high": 100.50,
            "swing_low": 80.25,
        }
        
        result = client.save_stock_score("TEST", test_data, scan_date=date.today())
        print(f"   ✅ Test record saved: {result}")
        
        print("\n3. Testing query...")
        top_stocks = client.get_top_stocks(limit=10)
        print(f"   ✅ Found {len(top_stocks)} records")
        
        if top_stocks:
            print("\n   Latest records:")
            for stock in top_stocks[:5]:
                print(f"   - {stock['symbol']}: {stock['score']}/11 ({stock['scan_date']})")
        
        print("\n" + "=" * 60)
        print("  ✅ All tests passed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure you:")
        print("1. Created a Supabase project")
        print("2. Executed the schema SQL")
        print("3. Configured scanner/.env with correct credentials")
        sys.exit(1)

if __name__ == "__main__":
    test_connection()
