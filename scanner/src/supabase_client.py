import os
from datetime import date
from typing import Dict, List
import httpx
from dotenv import load_dotenv

load_dotenv()

class SupabaseClient:
    def __init__(self):
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        disable_ssl = os.getenv("DISABLE_SSL_VERIFY", "false").lower() == "true"
        
        if not url or not key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set")
        
        # Crear cliente httpx con o sin verificación SSL
        if disable_ssl:
            self.http_client = httpx.Client(verify=False, timeout=30.0)
        else:
            self.http_client = httpx.Client(timeout=30.0)
        
        self.url = url
        self.key = key
        self.headers = {
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Prefer": "resolution=merge-duplicates"
        }
    
    def save_stock_score(self, symbol: str, score_data: Dict, scan_date: date = None) -> Dict:
        if scan_date is None:
            scan_date = date.today()
        
        list_names = score_data.get("list_names", [])
        list_name = ", ".join(list_names) if list_names else None
        
        data = {
            "symbol": symbol,
            "scan_date": scan_date.isoformat(),
            "score": score_data.get("total_score", 0),
            "passed_filter": score_data.get("passed_filter", False),
            "market_bias_score": score_data.get("market_bias_score", 0),
            "market_bias_timeframe": score_data.get("market_bias_timeframe", None),
            "fibonacci_score": score_data.get("fibonacci_score", 0),
            "fibonacci_zone": score_data.get("fibonacci_zone", None),
            "bx_color": score_data.get("bx_trender_color", None),
            "swing_high": score_data.get("swing_high", None),
            "swing_low": score_data.get("swing_low", None),
            "list_name": list_name,
        }
        
        result = self.client.table("stock_scores").upsert(data).execute()
        return result.data[0] if result.data else {}
    
    def save_stock_scores_batch(self, scores: Dict[str, Dict], scan_date: date = None) -> int:
        if scan_date is None:
            scan_date = date.today()
        
        data_list = []
        for symbol, score_data in scores.items():
            if score_data.get('swing_high') and str(score_data['swing_high']) == 'nan':
                score_data['swing_high'] = None
            if score_data.get('swing_low') and str(score_data['swing_low']) == 'nan':
                score_data['swing_low'] = None
            
            list_names = score_data.get("list_names", [])
            list_name = ", ".join(list_names) if list_names else None
            
            data = {
                "symbol": symbol,
                "scan_date": scan_date.isoformat(),
                "score": score_data.get("total_score", 0),
                "passed_filter": score_data.get("passed_filter", False),
                "market_bias_score": score_data.get("market_bias_score", 0),
                "market_bias_timeframe": score_data.get("market_bias_timeframe", None),
                "fibonacci_score": score_data.get("fibonacci_score", 0),
                "fibonacci_zone": score_data.get("fibonacci_zone", None),
                "bx_color": score_data.get("bx_trender_color", None),
                "swing_high": score_data.get("swing_high", None),
                "swing_low": score_data.get("swing_low", None),
                "list_name": list_name,
            }
            data_list.append(data)
        
        # Usar httpx directamente en lugar del cliente de Supabase
        try:
            response = self.http_client.post(
                f"{self.url}/rest/v1/stock_scores?on_conflict=symbol,scan_date",
                headers=self.headers,
                json=data_list
            )
            
            response.raise_for_status()
            
            if response.status_code in [200, 201, 204]:
                return len(data_list)
            
            return 0
        except httpx.HTTPStatusError as e:
            print(f"   ❌ HTTP Error {e.response.status_code}: {e.response.text[:500]}")
            raise
    
    def get_top_stocks(self, scan_date: date = None, limit: int = 50) -> List[Dict]:
        if scan_date is None:
            scan_date = date.today()
        
        result = self.client.table("stock_scores")\
            .select("*")\
            .eq("scan_date", scan_date.isoformat())\
            .order("score", desc=True)\
            .limit(limit)\
            .execute()
        
        return result.data
    
    def get_stock_history(self, symbol: str, days: int = 30) -> List[Dict]:
        result = self.client.table("stock_scores")\
            .select("*")\
            .eq("symbol", symbol)\
            .order("scan_date", desc=True)\
            .limit(days)\
            .execute()
        
        return result.data