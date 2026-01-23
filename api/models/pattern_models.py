"""
Pydantic models for pattern matching API requests and responses.
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from enum import Enum


class TimeframeEnum(str, Enum):
    """Timeframe options for stock data."""
    DAILY = "1d"
    WEEKLY = "1wk"
    MONTHLY = "1mo"


class PatternMatchRequest(BaseModel):
    """
    Request model for pattern matching endpoint.

    Attributes:
        pattern: List of normalized Y values from user-drawn pattern
        num_points: Number of points in the pattern (must match len(pattern))
        symbols: List of stock symbols to search (optional, uses default list if not provided)
        timeframe: Timeframe for historical data (default: 1d)
        period: Period of historical data (default: 6mo for 100-200 days)
        top_n: Number of top matches to return (default: 10)
        step_size: Sliding window step size (default: 1)
    """
    pattern: List[float] = Field(
        ...,
        description="Normalized Y values from the drawn pattern",
        min_length=10,
        max_length=200
    )
    num_points: int = Field(
        ...,
        description="Number of points in the pattern",
        ge=10,
        le=200
    )
    symbols: Optional[List[str]] = Field(
        None,
        description="Stock symbols to search (optional)",
        max_length=50
    )
    timeframe: TimeframeEnum = Field(
        default=TimeframeEnum.WEEKLY,
        description="Timeframe for stock data"
    )
    period: str = Field(
        default="2y",
        description="Period of historical data (e.g., '6mo', '1y', '2y')"
    )
    top_n: int = Field(
        default=10,
        description="Number of top matches to return",
        ge=1,
        le=50
    )
    step_size: int = Field(
        default=1,
        description="Sliding window step size",
        ge=1,
        le=10
    )

    @field_validator('pattern')
    @classmethod
    def validate_pattern(cls, v: List[float]) -> List[float]:
        """Validate that pattern contains valid numbers."""
        if not v:
            raise ValueError("Pattern cannot be empty")

        # Check for NaN or infinite values
        import math
        for i, val in enumerate(v):
            if math.isnan(val) or math.isinf(val):
                raise ValueError(f"Pattern contains invalid value at index {i}: {val}")

        return v

    @field_validator('num_points')
    @classmethod
    def validate_num_points(cls, v: int, info) -> int:
        """Validate that num_points matches pattern length."""
        # Note: In Pydantic v2, we access other fields via info.data
        if 'pattern' in info.data:
            pattern = info.data['pattern']
            if len(pattern) != v:
                raise ValueError(
                    f"num_points ({v}) must match pattern length ({len(pattern)})"
                )
        return v


class StockMatchResult(BaseModel):
    """
    Individual stock match result.

    Attributes:
        symbol: Stock ticker symbol
        distance: DTW distance (lower = better)
        similarity_score: Normalized similarity score (0-1, higher = better)
        correlation: Pearson correlation coefficient (-1 to 1)
        start_date: Start date of matched pattern
        end_date: End date of matched pattern
        matched_prices: List of prices that matched the pattern
    """
    symbol: str = Field(..., description="Stock ticker symbol")
    distance: float = Field(..., description="DTW distance (lower = better)", ge=0)
    similarity_score: float = Field(
        ...,
        description="Similarity score (0-1, higher = better)",
        ge=0,
        le=1
    )
    correlation: Optional[float] = Field(
        None,
        description="Pearson correlation coefficient",
        ge=-1,
        le=1
    )
    start_date: str = Field(..., description="Start date of matched pattern")
    end_date: str = Field(..., description="End date of matched pattern")
    matched_prices: List[float] = Field(
        ...,
        description="Closing prices of the matched window"
    )


class PatternMatchResponse(BaseModel):
    """
    Response model for pattern matching endpoint.

    Attributes:
        success: Whether the request was successful
        message: Human-readable message
        matches: List of stock matches sorted by similarity
        pattern_stats: Statistics about the input pattern
        search_params: Parameters used for the search
    """
    success: bool = Field(..., description="Whether the request was successful")
    message: str = Field(..., description="Human-readable message")
    matches: List[StockMatchResult] = Field(
        default_factory=list,
        description="List of matching stocks sorted by similarity"
    )
    pattern_stats: Optional[dict] = Field(
        None,
        description="Statistics about the input pattern"
    )
    search_params: Optional[dict] = Field(
        None,
        description="Parameters used for the search"
    )


class ErrorResponse(BaseModel):
    """
    Error response model.

    Attributes:
        success: Always False for errors
        message: Error message
        error_type: Type of error
        details: Additional error details
    """
    success: bool = Field(default=False, description="Always False for errors")
    message: str = Field(..., description="Error message")
    error_type: str = Field(..., description="Type of error")
    details: Optional[dict] = Field(None, description="Additional error details")