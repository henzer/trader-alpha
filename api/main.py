from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import numpy as np

from src.providers import YFinanceProvider
from src.models import Timeframe
from src.scoring import calculate_stock_score
from src.indicators import calculate_fibonacci_retracement, calculate_market_bias, calculate_bx_trender
from src.stock_chart import StockChart

# Pattern matching imports
from models.pattern_models import (
    PatternMatchRequest,
    PatternMatchResponse,
    StockMatchResult,
    ErrorResponse,
    TimeframeEnum
)
from utils.pattern_normalization import prepare_pattern, calculate_pattern_stats, validate_pattern
from utils.dtw_matcher import match_pattern_to_multiple_stocks

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


# Default list of popular stocks to search if none provided
DEFAULT_STOCK_SYMBOLS = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "META", "TSLA", "NVDA", "JPM",
    "V", "WMT", "JNJ", "PG", "MA", "HD", "DIS", "NFLX", "PYPL", "ADBE",
    "CRM", "CSCO", "INTC", "AMD", "QCOM", "TXN", "ORCL", "IBM", "UBER",
    "BA", "GE", "CAT"
]


@app.post("/pattern/match", response_model=PatternMatchResponse)
async def match_pattern(request: PatternMatchRequest):
    """
    Match a user-drawn pattern against historical stock data using DTW.

    This endpoint:
    1. Receives a normalized pattern from the frontend
    2. Fetches historical data for specified (or default) stock symbols
    3. Uses Dynamic Time Warping to find similar patterns
    4. Returns top N matches ranked by similarity

    Args:
        request: PatternMatchRequest with pattern data and search parameters

    Returns:
        PatternMatchResponse with list of matching stocks

    Raises:
        HTTPException: If validation fails or processing error occurs
    """
    try:
        # Convert pattern to numpy array
        pattern_array = np.array(request.pattern)

        # Validate pattern
        is_valid, error_msg = validate_pattern(pattern_array, min_points=10, min_std=0.01)
        if not is_valid:
            return PatternMatchResponse(
                success=False,
                message=f"Invalid pattern: {error_msg}",
                matches=[],
                pattern_stats=calculate_pattern_stats(pattern_array)
            )

        # Prepare pattern (already normalized from frontend, but ensure consistency)
        prepared_pattern = prepare_pattern(
            request.pattern,
            num_points=request.num_points
        )

        # Calculate pattern statistics for debugging
        pattern_stats = calculate_pattern_stats(prepared_pattern)

        # Determine which symbols to search
        symbols_to_search = request.symbols if request.symbols else DEFAULT_STOCK_SYMBOLS

        # Map TimeframeEnum to Timeframe
        timeframe_map = {
            TimeframeEnum.DAILY: Timeframe.DAILY,
            TimeframeEnum.WEEKLY: Timeframe.WEEKLY,
            TimeframeEnum.MONTHLY: Timeframe.MONTHLY,
        }
        timeframe = timeframe_map[request.timeframe]

        # Fetch historical data for all symbols
        print(f"Fetching data for {len(symbols_to_search)} symbols...")
        stock_data = {}

        for symbol in symbols_to_search:
            try:
                df = provider.get_stock_data(symbol, timeframe, period=request.period)
                if not df.empty and len(df) >= request.num_points:
                    stock_data[symbol] = df
            except Exception as e:
                print(f"Error fetching data for {symbol}: {str(e)}")
                continue

        if not stock_data:
            return PatternMatchResponse(
                success=False,
                message="No valid stock data found for the specified symbols",
                matches=[],
                pattern_stats=pattern_stats
            )

        print(f"Successfully fetched data for {len(stock_data)} symbols")

        # Perform pattern matching using DTW
        print("Running DTW pattern matching (recent patterns only)...")

        # Generate window size range around the pattern length
        base_size = request.num_points
        window_size_range = [
            max(20, base_size - 20),
            max(20, base_size - 10),
            base_size,
            min(200, base_size + 10),
            min(200, base_size + 20),
            min(200, base_size + 30)
        ]

        # Adjust max_days_ago based on timeframe
        # Weekly: Only search patterns ending this week or last week (max 1 week old)
        # Daily: Search patterns ending in last 3 days
        max_days_ago = 1 if timeframe == Timeframe.WEEKLY else 3

        matches = match_pattern_to_multiple_stocks(
            pattern=prepared_pattern,
            symbols=list(stock_data.keys()),
            dfs=stock_data,
            window_size=request.num_points,
            step_size=request.step_size,
            radius=10,
            top_n=request.top_n,
            recent_only=True,  # Only search patterns forming NOW
            window_size_range=window_size_range,
            max_days_ago=max_days_ago
        )

        # Convert matches to response format
        match_results = []
        for match in matches:
            match_results.append(
                StockMatchResult(
                    symbol=match.symbol,
                    distance=match.distance,
                    similarity_score=match.similarity_score,
                    correlation=match.correlation,
                    start_date=match.start_date,
                    end_date=match.end_date,
                    matched_prices=match.matched_prices
                )
            )

        # Prepare search parameters for response
        search_params = {
            "num_symbols_searched": len(stock_data),
            "timeframe": request.timeframe.value,
            "period": request.period,
            "pattern_length": request.num_points,
            "step_size": request.step_size,
            "top_n": request.top_n,
            "search_mode": "recent_only",
            "window_size_range": window_size_range
        }

        return PatternMatchResponse(
            success=True,
            message=f"Found {len(match_results)} matching patterns",
            matches=match_results,
            pattern_stats=pattern_stats,
            search_params=search_params
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Validation error: {str(e)}")
    except Exception as e:
        print(f"Error in pattern matching: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error matching pattern: {str(e)}")