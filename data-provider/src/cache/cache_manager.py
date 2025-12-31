import os
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from ..models import Timeframe


class CacheManager:
    def __init__(self, cache_dir: Optional[str] = None):
        if cache_dir is None:
            self.cache_dir = Path.home() / ".trader-alpha" / "cache"
        else:
            self.cache_dir = Path(cache_dir)
        
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.ttl_hours = {
            Timeframe.DAILY: 6,
            Timeframe.WEEKLY: 24,
            Timeframe.MONTHLY: 72
        }
    
    def _get_cache_path(self, symbol: str, timeframe: Timeframe, period: str) -> Path:
        today = datetime.now().strftime("%Y%m%d")
        filename = f"{symbol}_{timeframe.value}_{period}_{today}.parquet"
        return self.cache_dir / filename
    
    def _is_cache_valid(self, file_path: Path, timeframe: Timeframe) -> bool:
        if not file_path.exists():
            return False
        
        file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
        ttl = timedelta(hours=self.ttl_hours[timeframe])
        
        return datetime.now() - file_mtime < ttl
    
    def get(self, symbol: str, timeframe: Timeframe, period: str) -> Optional[pd.DataFrame]:
        cache_path = self._get_cache_path(symbol, timeframe, period)
        
        if self._is_cache_valid(cache_path, timeframe):
            try:
                df = pd.read_parquet(cache_path)
                return df
            except Exception as e:
                print(f"Error reading cache: {e}")
                return None
        
        return None
    
    def set(self, symbol: str, timeframe: Timeframe, period: str, data: pd.DataFrame) -> None:
        cache_path = self._get_cache_path(symbol, timeframe, period)
        
        try:
            data.to_parquet(cache_path, index=True)
        except Exception as e:
            print(f"Error writing cache: {e}")
    
    def clear_old_cache(self, days: int = 7) -> None:
        cutoff = datetime.now() - timedelta(days=days)
        
        for file_path in self.cache_dir.glob("*.parquet"):
            file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
            if file_mtime < cutoff:
                file_path.unlink()
    
    def clear_all(self) -> None:
        for file_path in self.cache_dir.glob("*.parquet"):
            file_path.unlink()
