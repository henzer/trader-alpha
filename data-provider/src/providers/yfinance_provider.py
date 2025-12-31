import yfinance as yf
import pandas as pd
from typing import Dict, List, Optional
from .base import BaseDataProvider
from ..models import Timeframe
from ..cache import CacheManager


class YFinanceProvider(BaseDataProvider):
    def __init__(self, use_cache: bool = True, cache_dir: Optional[str] = None):
        self.use_cache = use_cache
        self.cache_manager = CacheManager(cache_dir) if use_cache else None
    
    def get_stock_data(
        self, 
        symbol: str, 
        timeframe: Timeframe, 
        period: str = "2y"
    ) -> pd.DataFrame:
        if self.use_cache and self.cache_manager:
            cached_data = self.cache_manager.get(symbol, timeframe, period)
            if cached_data is not None:
                return cached_data
        
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period, interval=timeframe.value)
            
            if df.empty:
                raise ValueError(f"No data returned for {symbol}")
            
            df.columns = df.columns.str.lower()
            
            if not self._validate_dataframe(df):
                raise ValueError(f"Invalid dataframe structure for {symbol}")
            
            if self.use_cache and self.cache_manager:
                self.cache_manager.set(symbol, timeframe, period, df)
            
            return df
            
        except Exception as e:
            raise Exception(f"Error fetching data for {symbol}: {str(e)}")
    
    def get_multiple_stocks(
        self, 
        symbols: List[str], 
        timeframe: Timeframe, 
        period: str = "2y"
    ) -> Dict[str, pd.DataFrame]:
        results = {}
        uncached_symbols = []
        
        for symbol in symbols:
            if self.use_cache and self.cache_manager:
                cached_data = self.cache_manager.get(symbol, timeframe, period)
                if cached_data is not None:
                    results[symbol] = cached_data
                else:
                    uncached_symbols.append(symbol)
            else:
                uncached_symbols.append(symbol)
        
        if uncached_symbols:
            print(f"   Downloading {len(uncached_symbols)} symbols in batch...")
            batch_data = self._download_batch(uncached_symbols, timeframe, period)
            results.update(batch_data)
        
        return results
    
    def _download_batch(
        self,
        symbols: List[str],
        timeframe: Timeframe,
        period: str = "2y"
    ) -> Dict[str, pd.DataFrame]:
        results = {}
        
        try:
            symbols_str = " ".join(symbols)
            data = yf.download(
                symbols_str,
                period=period,
                interval=timeframe.value,
                group_by='ticker',
                auto_adjust=True,
                threads=True,
                progress=False
            )
            
            if len(symbols) == 1:
                df = data.copy()
                df.columns = df.columns.str.lower()
                if not df.empty and self._validate_dataframe(df):
                    results[symbols[0]] = df
                    if self.use_cache and self.cache_manager:
                        self.cache_manager.set(symbols[0], timeframe, period, df)
            else:
                for symbol in symbols:
                    try:
                        if symbol in data.columns.levels[0]:
                            df = data[symbol].copy()
                            df.columns = df.columns.str.lower()
                            
                            if not df.empty and self._validate_dataframe(df):
                                results[symbol] = df
                                if self.use_cache and self.cache_manager:
                                    self.cache_manager.set(symbol, timeframe, period, df)
                    except Exception as e:
                        print(f"   ❌ {symbol}: {str(e)}")
                        continue
            
        except Exception as e:
            print(f"   ❌ Batch download failed: {e}")
            print(f"   ⚠️  Skipping individual fallback to avoid rate limiting")
        
        return results
    
    def clear_cache(self) -> None:
        if self.cache_manager:
            self.cache_manager.clear_all()
    
    def clear_old_cache(self, days: int = 7) -> None:
        if self.cache_manager:
            self.cache_manager.clear_old_cache(days)