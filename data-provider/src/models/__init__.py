from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field
import pandas as pd


class Timeframe(Enum):
    DAILY = "1d"
    WEEKLY = "1wk"
    MONTHLY = "1mo"


class StockDataRequest(BaseModel):
    symbol: str = Field(..., description="Stock ticker symbol (e.g., AAPL)")
    timeframe: Timeframe = Field(..., description="Timeframe for data")
    period: str = Field(default="2y", description="Period to fetch (e.g., 1y, 2y, 5y, max)")
    
    
class CacheMetadata(BaseModel):
    symbol: str
    timeframe: Timeframe
    period: str
    cached_at: str
    file_path: str
