"""
Dynamic Time Warping (DTW) utilities for pattern matching.

This module implements DTW-based pattern matching with sliding window support
for finding similar price patterns in stock historical data.
"""

import numpy as np
import pandas as pd
from typing import List, Tuple, Optional
from dataclasses import dataclass
from scipy.spatial.distance import euclidean
from fastdtw import fastdtw


@dataclass
class PatternMatch:
    """
    Represents a single pattern match result.

    Attributes:
        symbol: Stock ticker symbol
        distance: DTW distance (lower = better match)
        similarity_score: Normalized similarity score (0-1, higher = better)
        start_idx: Start index of the matching window in the stock data
        end_idx: End index of the matching window in the stock data
        start_date: Start date of the matching pattern
        end_date: End date of the matching pattern
        matched_prices: The actual price values that matched
        correlation: Pearson correlation coefficient (optional)
    """
    symbol: str
    distance: float
    similarity_score: float
    start_idx: int
    end_idx: int
    start_date: str
    end_date: str
    matched_prices: List[float]
    correlation: Optional[float] = None


def calculate_dtw_distance(
    pattern1: np.ndarray,
    pattern2: np.ndarray,
    radius: int = 10
) -> float:
    """
    Calculate DTW distance between two patterns using FastDTW.

    FastDTW is an approximate DTW algorithm that runs in O(N) time
    complexity instead of O(N²).

    Args:
        pattern1: First pattern (normalized)
        pattern2: Second pattern (normalized)
        radius: FastDTW radius parameter (controls approximation quality)

    Returns:
        DTW distance value (lower = more similar)
    """
    # Reshape for fastdtw (expects 2D arrays)
    p1 = pattern1.reshape(-1, 1)
    p2 = pattern2.reshape(-1, 1)

    # Calculate DTW distance using Euclidean distance metric
    distance, _ = fastdtw(p1, p2, radius=radius, dist=euclidean)

    return float(distance)


def sliding_window_match(
    pattern: np.ndarray,
    stock_prices: np.ndarray,
    window_size: int,
    step_size: int = 1,
    radius: int = 10
) -> List[Tuple[int, int, float]]:
    """
    Perform sliding window DTW matching over stock price history.

    Args:
        pattern: User-drawn pattern (normalized)
        stock_prices: Historical stock prices (normalized)
        window_size: Size of the sliding window (should match pattern length)
        step_size: How many points to slide the window each iteration
        radius: FastDTW radius parameter

    Returns:
        List of tuples (start_idx, end_idx, dtw_distance) for each window
    """
    matches = []
    n = len(stock_prices)

    # Slide window across the entire price history
    for i in range(0, n - window_size + 1, step_size):
        window_end = i + window_size
        window_data = stock_prices[i:window_end]

        # Calculate DTW distance between pattern and current window
        distance = calculate_dtw_distance(pattern, window_data, radius=radius)

        matches.append((i, window_end - 1, distance))

    return matches


def find_best_match(
    pattern: np.ndarray,
    df: pd.DataFrame,
    window_size: Optional[int] = None,
    step_size: int = 1,
    radius: int = 10
) -> Optional[Tuple[int, int, float]]:
    """
    Find the best matching window in a stock's price history.

    Args:
        pattern: User-drawn pattern (normalized)
        df: Stock DataFrame with 'close' prices
        window_size: Size of sliding window (defaults to pattern length)
        step_size: Sliding window step size
        radius: FastDTW radius parameter

    Returns:
        Tuple of (start_idx, end_idx, dtw_distance) for best match, or None
    """
    if df.empty or 'close' not in df.columns:
        return None

    # Use pattern length as window size if not specified
    if window_size is None:
        window_size = len(pattern)

    # Extract and normalize closing prices
    from utils.pattern_normalization import normalize_zscore

    prices = df['close'].values
    normalized_prices = normalize_zscore(prices)

    # Perform sliding window matching
    matches = sliding_window_match(
        pattern=pattern,
        stock_prices=normalized_prices,
        window_size=window_size,
        step_size=step_size,
        radius=radius
    )

    if not matches:
        return None

    # Find the match with minimum DTW distance
    best_match = min(matches, key=lambda x: x[2])

    return best_match


def calculate_similarity_score(distance: float, max_distance: float = 100.0) -> float:
    """
    Convert DTW distance to a similarity score between 0 and 1.

    Args:
        distance: DTW distance value
        max_distance: Maximum expected distance (for normalization)

    Returns:
        Similarity score where 1.0 is perfect match, 0.0 is no match
    """
    # Normalize distance to 0-1 range, then invert
    # Using exponential decay for better scoring distribution
    similarity = np.exp(-distance / max_distance)

    return float(np.clip(similarity, 0.0, 1.0))


def calculate_correlation(pattern1: np.ndarray, pattern2: np.ndarray) -> float:
    """
    Calculate Pearson correlation coefficient between two patterns.

    Correlation provides an alternative measure of similarity that is
    less sensitive to small variations than DTW.

    Args:
        pattern1: First pattern
        pattern2: Second pattern

    Returns:
        Correlation coefficient (-1 to 1, where 1 is perfect positive correlation)
    """
    if len(pattern1) != len(pattern2):
        raise ValueError("Patterns must have the same length for correlation")

    if len(pattern1) < 2:
        return 0.0

    correlation = np.corrcoef(pattern1, pattern2)[0, 1]

    # Handle NaN (happens when one pattern has zero variance)
    if np.isnan(correlation):
        return 0.0

    return float(correlation)


def find_recent_pattern_match(
    pattern: np.ndarray,
    df: pd.DataFrame,
    window_sizes: List[int],
    max_days_ago: int = 3,
    radius: int = 10
) -> Optional[Tuple[int, int, float, int]]:
    """
    Find the best matching window that ENDS in the most recent data.

    This function searches for patterns that are forming NOW, not historical patterns.
    It tries multiple window sizes to find the best match that ends within the last few days.

    Args:
        pattern: User-drawn pattern (normalized)
        df: Stock DataFrame with 'close' prices
        window_sizes: List of window sizes to try (e.g., [30, 40, 50, 60])
        max_days_ago: How many days from the end to consider as "recent" (default: 3)
        radius: FastDTW radius parameter

    Returns:
        Tuple of (start_idx, end_idx, dtw_distance, window_size) for best match, or None
    """
    if df.empty or 'close' not in df.columns:
        return None

    from utils.pattern_normalization import normalize_zscore

    prices = df['close'].values
    normalized_prices = normalize_zscore(prices)

    n = len(prices)
    best_match = None
    best_distance = float('inf')

    # Try each window size
    for window_size in window_sizes:
        if window_size > n:
            continue  # Skip if window is larger than available data

        # Only look at windows that END in the last few days
        for end_offset in range(max_days_ago + 1):
            end_idx = n - 1 - end_offset  # Start from the last index, go back
            start_idx = end_idx - window_size + 1

            if start_idx < 0:
                continue  # Not enough data for this window

            # Extract window data
            window_data = normalized_prices[start_idx:end_idx + 1]

            # Resize pattern to match window size if needed
            if len(pattern) != window_size:
                # Resample pattern to match window size
                old_indices = np.linspace(0, len(pattern) - 1, len(pattern))
                new_indices = np.linspace(0, len(pattern) - 1, window_size)
                resized_pattern = np.interp(new_indices, old_indices, pattern)
            else:
                resized_pattern = pattern

            # Calculate DTW distance
            distance = calculate_dtw_distance(resized_pattern, window_data, radius=radius)

            # Keep track of best match
            if distance < best_distance:
                best_distance = distance
                best_match = (start_idx, end_idx, distance, window_size)

    return best_match


def match_pattern_to_stock(
    pattern: np.ndarray,
    symbol: str,
    df: pd.DataFrame,
    window_size: Optional[int] = None,
    step_size: int = 1,
    radius: int = 10,
    include_correlation: bool = True,
    recent_only: bool = True,
    window_size_range: Optional[List[int]] = None,
    max_days_ago: int = 3
) -> Optional[PatternMatch]:
    """
    Match a pattern against a single stock's historical data.

    Args:
        pattern: User-drawn pattern (normalized)
        symbol: Stock ticker symbol
        df: Stock DataFrame with price data
        window_size: Size of sliding window (defaults to pattern length)
        step_size: Sliding window step size
        radius: FastDTW radius parameter
        include_correlation: Whether to calculate correlation coefficient
        recent_only: If True, only search for patterns ending in recent data (default: True)
        window_size_range: List of window sizes to try for recent search (default: [30,40,50,60])

    Returns:
        PatternMatch object with match details, or None if no valid match
    """
    if df.empty:
        return None

    # Recent-only mode: search for patterns forming NOW
    if recent_only:
        if window_size_range is None:
            # Default: try window sizes around the pattern length
            base_size = len(pattern)
            window_size_range = [
                max(20, base_size - 20),
                max(20, base_size - 10),
                base_size,
                base_size + 10,
                base_size + 20
            ]

        match_result = find_recent_pattern_match(
            pattern=pattern,
            df=df,
            window_sizes=window_size_range,
            max_days_ago=max_days_ago,
            radius=radius
        )

        if match_result is None:
            return None

        start_idx, end_idx, distance, matched_window_size = match_result

    # Historical mode: search entire history
    else:
        match_result = find_best_match(
            pattern=pattern,
            df=df,
            window_size=window_size,
            step_size=step_size,
            radius=radius
        )

        if match_result is None:
            return None

        start_idx, end_idx, distance = match_result
        matched_window_size = window_size or len(pattern)

    # Extract matched price segment
    matched_prices = df['close'].iloc[start_idx:end_idx + 1].values

    # Normalize matched prices for correlation calculation
    from utils.pattern_normalization import normalize_zscore
    normalized_matched = normalize_zscore(matched_prices)

    # Resize pattern to match window size for correlation
    if len(pattern) != len(normalized_matched):
        old_indices = np.linspace(0, len(pattern) - 1, len(pattern))
        new_indices = np.linspace(0, len(pattern) - 1, len(normalized_matched))
        resized_pattern = np.interp(new_indices, old_indices, pattern)
    else:
        resized_pattern = pattern

    # Calculate correlation if requested
    correlation = None
    if include_correlation:
        try:
            correlation = calculate_correlation(resized_pattern, normalized_matched)
        except Exception:
            correlation = None

    # Calculate similarity score
    similarity = calculate_similarity_score(distance)

    # Get dates for the matched window
    start_date = df.index[start_idx].strftime('%Y-%m-%d')
    end_date = df.index[end_idx].strftime('%Y-%m-%d')

    return PatternMatch(
        symbol=symbol,
        distance=distance,
        similarity_score=similarity,
        start_idx=start_idx,
        end_idx=end_idx,
        start_date=start_date,
        end_date=end_date,
        matched_prices=matched_prices.tolist(),
        correlation=correlation
    )


def match_pattern_to_multiple_stocks(
    pattern: np.ndarray,
    symbols: List[str],
    dfs: dict,
    window_size: Optional[int] = None,
    step_size: int = 1,
    radius: int = 10,
    top_n: int = 10,
    recent_only: bool = True,
    window_size_range: Optional[List[int]] = None,
    max_days_ago: int = 3
) -> List[PatternMatch]:
    """
    Match a pattern against multiple stocks and return top N matches.

    Args:
        pattern: User-drawn pattern (normalized)
        symbols: List of stock ticker symbols
        dfs: Dictionary mapping symbols to DataFrames
        window_size: Size of sliding window
        step_size: Sliding window step size
        radius: FastDTW radius parameter
        top_n: Number of top matches to return
        recent_only: If True, only search for patterns ending in recent data (default: True)
        window_size_range: List of window sizes to try for recent search
        max_days_ago: Max periods ago to consider as "recent" (1 for weekly, 3 for daily)

    Returns:
        List of PatternMatch objects sorted by similarity (best first)
    """
    matches = []

    for symbol in symbols:
        if symbol not in dfs or dfs[symbol].empty:
            continue

        match = match_pattern_to_stock(
            pattern=pattern,
            symbol=symbol,
            df=dfs[symbol],
            window_size=window_size,
            step_size=step_size,
            radius=radius,
            recent_only=recent_only,
            window_size_range=window_size_range,
            max_days_ago=max_days_ago
        )

        if match is not None:
            matches.append(match)

    # Sort by similarity score (highest first) and distance (lowest first)
    matches.sort(key=lambda x: (-x.similarity_score, x.distance))

    # Return top N matches
    return matches[:top_n]