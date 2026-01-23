"""
Pattern normalization utilities for pattern matching.

This module provides functions to normalize price patterns using Z-Score normalization,
allowing comparison of patterns based on their shape rather than absolute values.
"""

import numpy as np
import pandas as pd
from typing import List, Optional


def normalize_zscore(values: np.ndarray) -> np.ndarray:
    """
    Apply Z-Score normalization to a series of values.

    Formula: z = (x - μ) / σ
    where:
        - x is the original value
        - μ is the mean
        - σ is the standard deviation

    This normalization allows comparing patterns based on their shape rather than
    absolute values, making it scale-invariant.

    Args:
        values: Array of numerical values to normalize

    Returns:
        Array of Z-score normalized values

    Raises:
        ValueError: If input array is empty or has insufficient data
    """
    if len(values) == 0:
        raise ValueError("Cannot normalize empty array")

    if len(values) == 1:
        return np.array([0.0])

    # Calculate mean and standard deviation
    mean = np.mean(values)
    std = np.std(values)

    # Handle case where all values are the same (std = 0)
    if std == 0:
        return np.zeros_like(values)

    # Apply Z-score normalization
    normalized = (values - mean) / std

    return normalized


def extract_closing_prices(df: pd.DataFrame, num_points: Optional[int] = None) -> np.ndarray:
    """
    Extract closing prices from a stock DataFrame and optionally resample to N points.

    Args:
        df: DataFrame with stock data (must have 'close' column)
        num_points: If provided, resample to exactly this many points using linear interpolation

    Returns:
        Array of closing prices (optionally resampled)

    Raises:
        ValueError: If DataFrame is empty or missing 'close' column
    """
    if df.empty:
        raise ValueError("Cannot extract prices from empty DataFrame")

    if 'close' not in df.columns:
        raise ValueError("DataFrame must have 'close' column")

    # Get closing prices as numpy array
    prices = df['close'].values

    # If num_points is specified, resample using linear interpolation
    if num_points is not None and len(prices) != num_points:
        # Create evenly spaced indices for resampling
        old_indices = np.linspace(0, len(prices) - 1, len(prices))
        new_indices = np.linspace(0, len(prices) - 1, num_points)

        # Linear interpolation
        prices = np.interp(new_indices, old_indices, prices)

    return prices


def prepare_pattern(
    pattern_values: List[float],
    num_points: Optional[int] = None
) -> np.ndarray:
    """
    Prepare a user-drawn pattern for matching by resampling and normalizing.

    Args:
        pattern_values: List of Y values from the user-drawn pattern
        num_points: If provided, resample to exactly this many points

    Returns:
        Z-score normalized pattern ready for DTW comparison

    Raises:
        ValueError: If pattern is empty or invalid
    """
    if not pattern_values:
        raise ValueError("Pattern cannot be empty")

    # Convert to numpy array
    pattern = np.array(pattern_values)

    # Resample if needed
    if num_points is not None and len(pattern) != num_points:
        old_indices = np.linspace(0, len(pattern) - 1, len(pattern))
        new_indices = np.linspace(0, len(pattern) - 1, num_points)
        pattern = np.interp(new_indices, old_indices, pattern)

    # Apply Z-score normalization
    normalized = normalize_zscore(pattern)

    return normalized


def calculate_pattern_stats(values: np.ndarray) -> dict:
    """
    Calculate statistical properties of a pattern.

    Useful for debugging and validation.

    Args:
        values: Array of pattern values

    Returns:
        Dictionary with mean, std, min, max, range
    """
    if len(values) == 0:
        return {
            'mean': 0.0,
            'std': 0.0,
            'min': 0.0,
            'max': 0.0,
            'range': 0.0,
            'count': 0
        }

    return {
        'mean': float(np.mean(values)),
        'std': float(np.std(values)),
        'min': float(np.min(values)),
        'max': float(np.max(values)),
        'range': float(np.max(values) - np.min(values)),
        'count': len(values)
    }


def validate_pattern(
    values: np.ndarray,
    min_points: int = 10,
    min_std: float = 0.01
) -> tuple[bool, Optional[str]]:
    """
    Validate that a pattern is suitable for matching.

    Args:
        values: Pattern values to validate
        min_points: Minimum number of points required
        min_std: Minimum standard deviation required (ensures variation)

    Returns:
        Tuple of (is_valid, error_message)
    """
    if len(values) < min_points:
        return False, f"Pattern must have at least {min_points} points"

    std = np.std(values)
    if std < min_std:
        return False, f"Pattern has insufficient variation (std={std:.4f})"

    if np.any(np.isnan(values)):
        return False, "Pattern contains NaN values"

    if np.any(np.isinf(values)):
        return False, "Pattern contains infinite values"

    return True, None