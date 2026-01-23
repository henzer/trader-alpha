
# Pattern Matching Feature - Documentation

## Overview

This feature allows users to draw a price pattern on a canvas and find stocks that match that pattern using Dynamic Time Warping (DTW) algorithm.

## Architecture

```
Frontend (React/Next.js)
    ↓ (User draws pattern)
    ↓ (Simplify to N points)
    ↓ (Normalize Y values)
    ↓
API Endpoint (/pattern/match)
    ↓ (Receive pattern)
    ↓ (Fetch stock data via YFinanceProvider)
    ↓ (Apply Z-Score normalization)
    ↓ (Run DTW with sliding window)
    ↓ (Return top N matches)
    ↓
Frontend (Display results)
```

## Installation

### 1. Install Python dependencies

```bash
cd api
pip install -r requirements.txt
```

New dependencies added:
- `fastdtw>=0.3.4` - Fast DTW algorithm implementation
- `scipy>=1.11.0` - Scientific computing library (for distance metrics)

### 2. Verify installation

```bash
python test_pattern_endpoint.py
```

This will test the pattern matching functionality without starting the API server.

## API Endpoint

### POST `/pattern/match`

Match a user-drawn pattern against historical stock data.

**Request Body:**

```json
{
  "pattern": [0.12, -0.45, 0.23, ...],  // Z-score normalized Y values
  "num_points": 50,                      // Number of points (must match pattern length)
  "symbols": ["AAPL", "MSFT", ...],     // Optional: stocks to search
  "timeframe": "1d",                     // "1d", "1wk", or "1mo"
  "period": "6mo",                       // "1mo", "3mo", "6mo", "1y", "2y", etc.
  "top_n": 10,                           // Number of top matches to return
  "step_size": 1                         // Sliding window step size
}
```

**Response:**

```json
{
  "success": true,
  "message": "Found 10 matching patterns",
  "matches": [
    {
      "symbol": "AAPL",
      "distance": 12.45,
      "similarity_score": 0.92,
      "correlation": 0.88,
      "start_date": "2024-01-15",
      "end_date": "2024-03-15",
      "matched_prices": [150.23, 152.45, ...]
    }
  ],
  "pattern_stats": {
    "mean": 0.0,
    "std": 1.0,
    "min": -2.1,
    "max": 2.3,
    "range": 4.4,
    "count": 50
  },
  "search_params": {
    "num_symbols_searched": 30,
    "timeframe": "1d",
    "period": "6mo",
    "pattern_length": 50,
    "step_size": 1,
    "top_n": 10
  }
}
```

## Files Created

### Backend (API)

```
api/
├── utils/
│   ├── __init__.py
│   ├── pattern_normalization.py    # Z-Score normalization utilities
│   └── dtw_matcher.py              # DTW matching with sliding window
├── models/
│   ├── __init__.py
│   └── pattern_models.py           # Pydantic request/response models
├── main.py                          # FastAPI app (endpoint added)
├── requirements.txt                 # Updated with DTW dependencies
├── test_pattern_endpoint.py        # Test script
└── PATTERN_MATCHING_README.md      # This file
```

### Frontend (webapp)

```
webapp/
├── app/
│   └── draw/
│       └── page.tsx                 # Draw pattern page
├── components/
│   └── PatternCanvas.tsx            # Canvas drawing component
├── lib/
│   └── canvas-utils.ts              # Pattern simplification & normalization
└── app/layout.tsx                   # Updated with "Draw Pattern" nav link
```

## Usage

### 1. Start the API server

```bash
cd api
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Start the frontend

```bash
cd webapp
npm run dev
```

### 3. Use the feature

1. Navigate to `http://localhost:3000/draw`
2. Draw a pattern on the canvas
3. Click "Search Patterns"
4. View matching stocks

## Algorithm Details

### Pattern Normalization (Z-Score)

Both the user's drawn pattern and stock price data are normalized using Z-Score:

```
z = (x - μ) / σ
```

Where:
- `x` = original value
- `μ` = mean
- `σ` = standard deviation

This makes the comparison scale-invariant, focusing on **shape** rather than absolute values.

### Dynamic Time Warping (DTW)

DTW measures similarity between two sequences that may vary in speed/timing. It's ideal for pattern matching because:

1. **Flexible alignment**: Handles patterns that are "stretched" or "compressed" in time
2. **Shape-based**: Focuses on the overall shape/trend
3. **Robust**: Works well with noisy data

**Recent Pattern Matching (Default Mode):**
- **ONLY searches patterns forming NOW** (ending in the last 3 days)
- Tries multiple window sizes (pattern_length ± 20 days)
- Example: If you draw a 50-point pattern, it searches windows of 30, 40, 50, 60, 70 days
- All windows must END at the most recent data (today or 1-3 days ago)
- This finds stocks where the pattern is **currently forming**

**Why Multiple Window Sizes?**
Your drawn pattern might represent:
- A 30-day price movement
- A 40-day price movement
- A 50-day price movement
- Or any other duration

The algorithm tests different durations to find the best match, but ALL matches end at "today".

**Historical Mode (Optional):**
- Searches the entire price history (last 6 months)
- Finds the best match anywhere in the data
- Useful for backtesting, not for current trading signals

**Example:**

```
Stock Price History (180 days):
|------------------------------------------|-------|
Day 1                                    Day 150  Day 180 (Today)

RECENT MODE (Default):
Only searches here: |----|  (matches ending at day 177-180)
                      Day 130-180

HISTORICAL MODE:
Searches everywhere: |------------------------------------------|
                     Day 1-180
```

When you draw a 50-day pattern, Recent Mode will:
1. Try 30-day window ending today → Calculate DTW
2. Try 40-day window ending today → Calculate DTW
3. Try 50-day window ending today → Calculate DTW
4. Try 60-day window ending today → Calculate DTW
5. Try 70-day window ending today → Calculate DTW
6. Return the window with the LOWEST DTW distance

**Result:** "This stock has a pattern similar to yours forming over the last X days"

### Similarity Score

DTW distance is converted to a 0-1 similarity score using exponential decay:

```
similarity = e^(-distance / max_distance)
```

Where higher scores (closer to 1.0) indicate better matches.

## Performance Considerations

### Caching
- YFinanceProvider uses file-based caching (Parquet format)
- Cache TTL: 6 hours (daily), 24 hours (weekly), 72 hours (monthly)
- Significantly reduces API calls to Yahoo Finance

### Optimization Tips

1. **Reduce step_size**: Use `step_size=5` for faster searches (less accurate)
2. **Limit symbols**: Search fewer stocks for faster results
3. **Use weekly/monthly data**: Fewer data points = faster DTW calculation
4. **Enable caching**: Set `use_cache=True` in YFinanceProvider

### Typical Performance

- **Single stock match**: ~0.1-0.5 seconds
- **10 stocks (6 months, daily)**: ~2-5 seconds
- **30 stocks (6 months, daily)**: ~5-15 seconds

## Default Stock List

If no symbols are provided, the endpoint searches these 30 popular stocks:

```python
AAPL, MSFT, GOOGL, AMZN, META, TSLA, NVDA, JPM, V, WMT,
JNJ, PG, MA, HD, DIS, NFLX, PYPL, ADBE, CRM, CSCO,
INTC, AMD, QCOM, TXN, ORCL, IBM, UBER, BA, GE, CAT
```

## Troubleshooting

### Error: "Pattern has insufficient variation"
- The drawn pattern is too flat (all values similar)
- Draw a pattern with more variation (ups and downs)

### Error: "No valid stock data found"
- Check internet connection
- Verify symbols are valid ticker symbols
- Try a different period (e.g., "1y" instead of "6mo")

### Slow performance
- Reduce `step_size` (e.g., 3-5 instead of 1)
- Search fewer symbols
- Use weekly or monthly timeframe
- Enable caching

### CORS errors
- Ensure API is running with CORS enabled (already configured)
- Check `NEXT_PUBLIC_API_URL` environment variable in frontend

## Testing

### Test the backend only:

```bash
cd api
python test_pattern_endpoint.py
```

### Test the full API endpoint:

```bash
# Terminal 1: Start API
cd api
uvicorn main:app --reload

# Terminal 2: Test with curl
curl -X POST http://localhost:8000/pattern/match \
  -H "Content-Type: application/json" \
  -d '{
    "pattern": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
    "num_points": 10,
    "top_n": 5
  }'
```

## Future Enhancements

Possible improvements:

1. **Multiple distance metrics**: Add Euclidean, correlation-based matching
2. **Pattern library**: Save and reuse common patterns
3. **Real-time matching**: WebSocket-based live pattern matching
4. **Advanced filters**: Filter by sector, market cap, volume, etc.
5. **Pattern visualization**: Show matched patterns overlaid on charts
6. **Stock scoring integration**: Combine DTW with existing scoring system

## References

- FastDTW Paper: https://cs.fit.edu/~pkc/papers/tdm04.pdf
- DTW Tutorial: https://en.wikipedia.org/wiki/Dynamic_time_warping
- yfinance Documentation: https://pypi.org/project/yfinance/
