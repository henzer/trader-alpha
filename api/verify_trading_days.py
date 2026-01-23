"""
Verify if yfinance returns only trading days or includes weekends/holidays.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.providers import YFinanceProvider
from src.models import Timeframe
import pandas as pd


def check_trading_days():
    """Check if yfinance data includes non-trading days."""

    print("=" * 80)
    print("VERIFYING IF YFINANCE INCLUDES NON-TRADING DAYS")
    print("=" * 80)

    provider = YFinanceProvider(use_cache=False)

    # Get recent data for QCOM
    df = provider.get_stock_data("QCOM", Timeframe.DAILY, period="3mo")

    print(f"\nTotal rows in DataFrame: {len(df)}")
    print(f"Date range: {df.index[0]} to {df.index[-1]}")

    # Check for weekends
    print("\n" + "=" * 80)
    print("CHECKING FOR WEEKENDS (Saturday=5, Sunday=6)")
    print("=" * 80)

    weekends = []
    for date in df.index:
        day_of_week = date.dayofweek  # Monday=0, Sunday=6
        if day_of_week >= 5:  # Saturday or Sunday
            weekends.append((date, day_of_week))

    if weekends:
        print(f"\n⚠️  FOUND {len(weekends)} WEEKEND DAYS IN DATA:")
        for date, dow in weekends[:10]:  # Show first 10
            day_name = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][dow]
            print(f"   {date.strftime('%Y-%m-%d')} ({day_name})")
        if len(weekends) > 10:
            print(f"   ... and {len(weekends) - 10} more")
    else:
        print("\n✓ NO WEEKEND DAYS FOUND - Data contains only weekdays")

    # Check for consecutive dates (should have gaps)
    print("\n" + "=" * 80)
    print("CHECKING FOR DATE GAPS (should have gaps for weekends/holidays)")
    print("=" * 80)

    gaps = []
    for i in range(1, min(50, len(df))):  # Check first 50 dates
        prev_date = df.index[i-1]
        curr_date = df.index[i]
        days_diff = (curr_date - prev_date).days

        if days_diff > 1:
            gaps.append((prev_date, curr_date, days_diff))

    if gaps:
        print(f"\n✓ FOUND {len(gaps)} DATE GAPS (normal for trading data):")
        for prev, curr, diff in gaps[:10]:
            print(f"   {prev.strftime('%Y-%m-%d')} -> {curr.strftime('%Y-%m-%d')} ({diff} calendar days)")
    else:
        print("\n⚠️  NO DATE GAPS FOUND - Data appears to be consecutive calendar days!")

    # Sample dates around a known holiday period (Christmas/New Year)
    print("\n" + "=" * 80)
    print("CHECKING DECEMBER/JANUARY DATES (Holiday period)")
    print("=" * 80)

    # Filter dates in Dec 2025 and Jan 2026
    dec_jan_dates = df[(df.index >= '2025-12-01') & (df.index <= '2026-01-31')]

    if not dec_jan_dates.empty:
        print(f"\nFound {len(dec_jan_dates)} trading days in Dec 2025 - Jan 2026:")
        print("\nAll dates in this period:")
        for i, date in enumerate(dec_jan_dates.index):
            day_name = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][date.dayofweek]
            close_price = dec_jan_dates['close'].iloc[i]
            print(f"   {date.strftime('%Y-%m-%d')} ({day_name}) - Close: ${close_price:.2f}")

        # Count specific dates we expect to be closed
        holidays_to_check = [
            ('2025-12-25', 'Christmas'),
            ('2026-01-01', 'New Year'),
        ]

        print("\n" + "-" * 80)
        print("Checking known holidays:")
        for date_str, holiday_name in holidays_to_check:
            if pd.Timestamp(date_str) in dec_jan_dates.index:
                print(f"   ⚠️  {holiday_name} ({date_str}) IS IN DATA (unexpected!)")
            else:
                print(f"   ✓ {holiday_name} ({date_str}) NOT in data (correct)")
    else:
        print("\nNo data found in Dec 2025 - Jan 2026 period")

    # Final verification: Count trading days between two dates
    print("\n" + "=" * 80)
    print("MANUAL COUNT: Dec 10, 2025 to Jan 23, 2026")
    print("=" * 80)

    try:
        start_date = pd.Timestamp('2025-12-10')
        end_date = pd.Timestamp('2026-01-23')

        mask = (df.index >= start_date) & (df.index <= end_date)
        period_data = df[mask]

        print(f"\nTrading days in this exact period: {len(period_data)}")
        print(f"Calendar days in this period: {(end_date - start_date).days + 1}")

        if len(period_data) > 0:
            print(f"\nFirst few dates:")
            for i, date in enumerate(period_data.index[:5]):
                day_name = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][date.dayofweek]
                print(f"   {date.strftime('%Y-%m-%d')} ({day_name})")

            print(f"\nLast few dates:")
            for i, date in enumerate(period_data.index[-5:]):
                day_name = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][date.dayofweek]
                print(f"   {date.strftime('%Y-%m-%d')} ({day_name})")
    except Exception as e:
        print(f"Could not verify specific period: {e}")

    print("\n" + "=" * 80)
    print("CONCLUSION")
    print("=" * 80)

    if not weekends and gaps:
        print("\n✓ yfinance returns ONLY TRADING DAYS")
        print("  - No weekends found")
        print("  - Date gaps present (normal)")
        print("  - Holidays appear to be filtered")
    elif weekends or not gaps:
        print("\n⚠️  WARNING: yfinance may include NON-TRADING DAYS")
        print("  - Need to filter data before DTW matching")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    try:
        check_trading_days()
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
