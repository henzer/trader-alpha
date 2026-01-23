"""
Test script for the pattern matching endpoint.

This script tests the pattern matching functionality without running the full API server.
"""

import numpy as np
import sys
from pathlib import Path

# Add parent directory to path to import from src
sys.path.insert(0, str(Path(__file__).parent))

from utils.pattern_normalization import prepare_pattern, calculate_pattern_stats, validate_pattern
from utils.dtw_matcher import match_pattern_to_multiple_stocks
from src.providers import YFinanceProvider
from src.models import Timeframe


def create_sample_pattern(pattern_type: str = "uptrend", num_points: int = 50) -> np.ndarray:
    """
    Create a sample pattern for testing.

    Args:
        pattern_type: Type of pattern ("uptrend", "downtrend", "v_shape", "wave")
        num_points: Number of points in the pattern

    Returns:
        Normalized pattern array
    """
    x = np.linspace(0, 1, num_points)

    if pattern_type == "uptrend":
        # Upward trend with some noise
        y = x + 0.1 * np.sin(x * 10) + np.random.normal(0, 0.05, num_points)
    elif pattern_type == "downtrend":
        # Downward trend with some noise
        y = 1 - x + 0.1 * np.sin(x * 10) + np.random.normal(0, 0.05, num_points)
    elif pattern_type == "v_shape":
        # V-shaped pattern
        y = np.abs(x - 0.5) * 2
        y = 1 - y  # Invert so V points up
        y += 0.1 * np.sin(x * 10) + np.random.normal(0, 0.05, num_points)
    elif pattern_type == "wave":
        # Sine wave pattern
        y = np.sin(x * 4 * np.pi) + np.random.normal(0, 0.05, num_points)
    else:
        raise ValueError(f"Unknown pattern type: {pattern_type}")

    # Normalize using Z-score
    pattern = prepare_pattern(y.tolist(), num_points=num_points)

    return pattern


def test_pattern_matching():
    """
    Test the pattern matching functionality.
    """
    print("=" * 80)
    print("PATTERN MATCHING TEST")
    print("=" * 80)

    # Create a sample pattern (uptrend)
    print("\n1. Creating sample pattern (uptrend)...")
    num_points = 50
    pattern = create_sample_pattern("uptrend", num_points=num_points)

    # Validate pattern
    is_valid, error_msg = validate_pattern(pattern, min_points=10, min_std=0.01)
    print(f"   Pattern valid: {is_valid}")
    if not is_valid:
        print(f"   Error: {error_msg}")
        return

    # Calculate pattern stats
    stats = calculate_pattern_stats(pattern)
    print(f"   Pattern stats:")
    print(f"   - Length: {stats['count']}")
    print(f"   - Mean: {stats['mean']:.4f}")
    print(f"   - Std Dev: {stats['std']:.4f}")
    print(f"   - Range: {stats['range']:.4f}")

    # Initialize data provider
    print("\n2. Initializing YFinance data provider...")
    provider = YFinanceProvider(use_cache=True)

    # Fetch data for a few test stocks
    test_symbols = ["AAPL", "MSFT", "GOOGL", "TSLA", "NVDA", "AMD", "META"]
    print(f"\n3. Fetching data for {len(test_symbols)} stocks...")
    print(f"   Symbols: {', '.join(test_symbols)}")

    stock_data = {}
    for symbol in test_symbols:
        try:
            print(f"   Fetching {symbol}...", end=" ")
            df = provider.get_stock_data(symbol, Timeframe.DAILY, period="6mo")
            if not df.empty and len(df) >= num_points:
                stock_data[symbol] = df
                print(f"✓ ({len(df)} days)")
            else:
                print("✗ (insufficient data)")
        except Exception as e:
            print(f"✗ ({str(e)})")

    if not stock_data:
        print("\n✗ ERROR: No stock data fetched. Cannot proceed with test.")
        return

    print(f"\n   Successfully fetched data for {len(stock_data)} stocks")

    # Perform pattern matching
    print("\n4. Running DTW pattern matching...")
    matches = match_pattern_to_multiple_stocks(
        pattern=pattern,
        symbols=list(stock_data.keys()),
        dfs=stock_data,
        window_size=num_points,
        step_size=1,
        radius=10,
        top_n=5
    )

    # Display results
    print("\n5. RESULTS:")
    print("=" * 80)

    if not matches:
        print("   No matches found.")
    else:
        print(f"   Found {len(matches)} matches:\n")
        for i, match in enumerate(matches, 1):
            print(f"   {i}. {match.symbol}")
            print(f"      Distance: {match.distance:.4f}")
            print(f"      Similarity: {match.similarity_score:.4f} ({match.similarity_score * 100:.1f}%)")
            if match.correlation is not None:
                print(f"      Correlation: {match.correlation:.4f}")
            print(f"      Date Range: {match.start_date} to {match.end_date}")
            print(f"      Price Range: ${match.matched_prices[0]:.2f} - ${match.matched_prices[-1]:.2f}")
            print()

    print("=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    try:
        test_pattern_matching()
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)