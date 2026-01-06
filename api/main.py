from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

from src.providers import YFinanceProvider
from src.models import Timeframe
from src.scoring import calculate_stock_score
from src.indicators import calculate_fibonacci_retracement, calculate_market_bias, calculate_bx_trender
from src.stock_chart import StockChart

app = FastAPI(title="Trader Alpha API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

provider = YFinanceProvider(use_cache=False)

@app.get("/")
def read_root():
    return {"message": "Trader Alpha API", "version": "1.0.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/chart/{symbol}", response_class=HTMLResponse)
async def get_chart(symbol: str):
    try:
        symbol = symbol.upper()
        
        df_daily = provider.get_stock_data(symbol, Timeframe.DAILY, period="2y")
        df_weekly = provider.get_stock_data(symbol, Timeframe.WEEKLY, period="2y")
        df_monthly = provider.get_stock_data(symbol, Timeframe.MONTHLY, period="2y")
        
        if df_daily.empty or df_weekly.empty or df_monthly.empty:
            raise HTTPException(status_code=404, detail=f"No data found for symbol {symbol}")
        
        score = calculate_stock_score(symbol, df_monthly, df_weekly, df_daily)
        fib_result = calculate_fibonacci_retracement(df_daily, lookback=50)
        
        bias_high_monthly, bias_low_monthly = calculate_market_bias(df_monthly, ha_len=20, ha_len2=7)
        bias_high_weekly, bias_low_weekly = calculate_market_bias(df_weekly, ha_len=20, ha_len2=7)
        
        bx_monthly = calculate_bx_trender(df_monthly, use_short=True, apply_t3=False)
        bx_weekly = calculate_bx_trender(df_weekly, use_short=True, apply_t3=False)
        
        score_data = {
            "total_score": score.score_breakdown.total_score,
            "passed_filter": score.score_breakdown.passed_filter,
            "market_bias_score": score.score_breakdown.market_bias_score,
            "market_bias_timeframe": score.score_breakdown.market_bias_timeframe.value if score.score_breakdown.market_bias_timeframe else None,
            "fibonacci_score": score.score_breakdown.fibonacci_score,
            "fibonacci_zone": score.score_breakdown.fibonacci_zone.value if score.score_breakdown.fibonacci_zone else None,
            "bx_trender_color": score.score_breakdown.bx_trender_color.value if score.score_breakdown.bx_trender_color else None,
        }
        
        chart = StockChart(symbol, df_daily)
        chart.set_score_data(score_data)
        chart.create_base_chart(with_bx_trender=True, bx_rows=3)
        
        chart.add_market_bias(
            bias_high_monthly, 
            bias_low_monthly,
            name="Monthly Market Bias",
            df_index=df_monthly.index,
            resample_to_daily=True,
            color='blue'
        )
        
        chart.add_market_bias(
            bias_high_weekly,
            bias_low_weekly,
            name="Weekly Market Bias",
            df_index=df_weekly.index,
            resample_to_daily=True,
            color='green'
        )
        
        if fib_result and fib_result.swing_high and fib_result.swing_low:
            chart.add_fibonacci(
                float(fib_result.swing_high),
                float(fib_result.swing_low),
                show_all_levels=True
            )
        
        chart.add_bx_trender(bx_monthly, row=2, name="Monthly BX-Trender", df_index=df_monthly.index, resample_to_daily=True)
        chart.add_bx_trender(bx_weekly, row=3, name="Weekly BX-Trender", df_index=df_weekly.index, resample_to_daily=True)
        
        chart.add_score_annotation()
        
        html_content = chart.fig.to_html(include_plotlyjs='cdn', full_html=True)
        
        return HTMLResponse(content=html_content)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating chart: {str(e)}")