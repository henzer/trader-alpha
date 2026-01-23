"""
Utility functions for the Trader Alpha API.
"""

from .pattern_normalization import (
    normalize_zscore,
    extract_closing_prices,
    prepare_pattern,
    calculate_pattern_stats,
    validate_pattern
)

from .dtw_matcher import (
    calculate_dtw_distance,
    sliding_window_match,
    find_best_match,
    find_recent_pattern_match,
    calculate_similarity_score,
    calculate_correlation,
    match_pattern_to_stock,
    match_pattern_to_multiple_stocks,
    PatternMatch
)

__all__ = [
    # Pattern normalization
    'normalize_zscore',
    'extract_closing_prices',
    'prepare_pattern',
    'calculate_pattern_stats',
    'validate_pattern',
    # DTW matching
    'calculate_dtw_distance',
    'sliding_window_match',
    'find_best_match',
    'find_recent_pattern_match',
    'calculate_similarity_score',
    'calculate_correlation',
    'match_pattern_to_stock',
    'match_pattern_to_multiple_stocks',
    'PatternMatch',
]