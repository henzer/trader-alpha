from abc import ABC, abstractmethod
import pandas as pd
from typing import Dict, List
from ..models import Timeframe


class BaseDataProvider(ABC):
    @abstractmethod
    def get_stock_data(
        self, 
        symbol: str, 
        timeframe: Timeframe, 
        period: str = "2y"
    ) -> pd.DataFrame:
        pass
    
    @abstractmethod
    def get_multiple_stocks(
        self, 
        symbols: List[str], 
        timeframe: Timeframe, 
        period: str = "2y"
    ) -> Dict[str, pd.DataFrame]:
        pass
    
    def _validate_dataframe(self, df: pd.DataFrame) -> bool:
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        return all(col in df.columns for col in required_columns)