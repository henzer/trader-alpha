from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class BXTrenderColor(Enum):
    LIME = "lime"
    DARK_GREEN = "dark_green"
    RED = "red"
    DARK_RED = "dark_red"


class Timeframe(Enum):
    DAILY = "1d"
    WEEKLY = "1wk"
    MONTHLY = "1mo"
    SIX_MONTH = "6mo"


class FibonacciZone(Enum):
    GOLDEN_ZONE = "golden_zone"
    SMART_MONEY_ZONE = "smart_money_zone"
    OUTSIDE = "outside"


class BXTrenderResult(BaseModel):
    value: float
    color: BXTrenderColor
    is_uptrend: bool
    
    
class MarketBiasResult(BaseModel):
    timeframe: Timeframe
    in_range: bool
    price: float
    bias_low: float
    bias_high: float


class FibonacciResult(BaseModel):
    swing_high: float
    swing_low: float
    current_price: float
    fib_0618: float
    fib_0786: float
    fib_0826: float
    zone: FibonacciZone
    in_smart_money_zone: bool


class ScoreBreakdown(BaseModel):
    market_bias_score: int = Field(ge=0, le=9)
    market_bias_timeframe: Optional[Timeframe] = None
    fibonacci_score: int = Field(ge=0, default=0, le=5)
    fibonacci_zone: Optional[FibonacciZone] = None
    total_score: int = Field(ge=0)
    passed_filter: bool
    bx_trender_color: Optional[BXTrenderColor] = None


class StockScore(BaseModel):
    symbol: str
    score_breakdown: ScoreBreakdown