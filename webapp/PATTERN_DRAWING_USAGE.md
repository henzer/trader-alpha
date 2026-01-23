# Pattern Drawing Feature - Usage Guide

## Overview

This feature allows you to draw a price pattern on a canvas and find stocks that have historically followed similar patterns using Dynamic Time Warping (DTW) algorithm.

## How to Use

### 1. Access the Drawing Page

Navigate to: `http://localhost:3000/draw`

Or click "Draw Pattern" in the navigation menu.

### 2. Draw Your Pattern

**Desktop:**
- Click and hold the left mouse button on the canvas
- Drag to draw your desired pattern
- Release the mouse button when done

**Mobile/Tablet:**
- Touch and hold on the canvas
- Drag your finger to draw the pattern
- Lift your finger when done

### 3. Adjust Settings (Optional)

**Number of Points:**
- Default: 50 points
- Range: 20-200 points
- More points = more detailed pattern matching (but slower)
- Fewer points = faster matching (but less precise)

### 4. Search for Matches

Click the **"Search Patterns"** button to:
1. Send your pattern to the backend API
2. Search through 30 popular stocks by default
3. Find the top 10 best matches using DTW algorithm

### 5. View Results

Results are displayed in order of similarity (best match first):

**For Each Match:**
- **Rank Badge** - Position in top 10
- **Stock Symbol** - Click to view full chart
- **Similarity Score** - Percentage match (higher = better)
- **DTW Distance** - Raw distance metric (lower = better)
- **Correlation** - Statistical correlation (-1 to 1)
- **Price Range** - Min/max prices during matched period
- **Pattern Move** - Price change % during the pattern
- **Mini Chart** - Visual preview of the matched pattern
- **Date Range** - When this pattern occurred

### 6. Clear and Redraw

Click **"Clear"** to:
- Erase the current drawing
- Reset the canvas
- Clear previous results
- Start a new pattern search

## Tips for Better Results

### Drawing Patterns

✅ **DO:**
- Draw smooth, continuous patterns
- Focus on the overall shape/trend
- Include 2-3 clear direction changes
- Make patterns at least 20 points long

❌ **AVOID:**
- Very short patterns (< 20 points)
- Completely flat/horizontal lines
- Too many rapid zigzags
- Extremely complex patterns

### Pattern Types That Work Well

1. **Uptrend** - Steady upward movement
2. **Downtrend** - Steady downward movement
3. **V-Shape** - Sharp decline followed by recovery
4. **Double Bottom** - Two dips with recovery
5. **Head & Shoulders** - Peak with smaller peaks on sides
6. **Cup & Handle** - U-shape with small dip

### Interpreting Results

**Similarity Score:**
- **90%+** - Excellent match, very similar pattern
- **80-90%** - Good match, strong similarity
- **70-80%** - Moderate match, noticeable similarity
- **< 70%** - Weak match, limited similarity

**Correlation:**
- **> 0.7** - Strong positive correlation
- **0.3-0.7** - Moderate correlation
- **< 0.3** - Weak correlation
- **Negative** - Inverse relationship

**DTW Distance:**
- **< 15** - Very close match
- **15-20** - Good match
- **20-30** - Moderate match
- **> 30** - Weak match

## Features

### Canvas Features
- ✅ Grid background for reference
- ✅ Real-time drawing preview
- ✅ Mouse and touch support
- ✅ Automatic pattern simplification
- ✅ Z-Score normalization

### Results Display
- ✅ Top 10 matches sorted by similarity
- ✅ Multiple similarity metrics (DTW, correlation, similarity %)
- ✅ Visual price chart preview
- ✅ Price statistics (range, % change)
- ✅ Date range of matched pattern
- ✅ Direct links to full stock charts

### Search Parameters
- ✅ Configurable point resolution (20-200)
- ✅ Searches 30 popular stocks by default
- ✅ Daily timeframe (6 months of data)
- ✅ Sliding window algorithm for best match

## Technical Details

### Pattern Processing

1. **Draw** - User draws on canvas (X, Y coordinates)
2. **Simplify** - Reduce to exactly N points via linear interpolation
3. **Extract** - Extract only Y values (prices)
4. **Normalize** - Apply Z-Score normalization: `z = (x - μ) / σ`
5. **Send** - POST to `/pattern/match` endpoint
6. **Match** - DTW sliding window over historical data
7. **Rank** - Sort by similarity score
8. **Display** - Show top 10 results

### Default Stocks Searched

AAPL, MSFT, GOOGL, AMZN, META, TSLA, NVDA, JPM, V, WMT,
JNJ, PG, MA, HD, DIS, NFLX, PYPL, ADBE, CRM, CSCO,
INTC, AMD, QCOM, TXN, ORCL, IBM, UBER, BA, GE, CAT

### API Endpoint

```
POST http://localhost:8000/pattern/match

Request:
{
  "pattern": [0.12, -0.45, 0.23, ...],  // Normalized Y values
  "num_points": 50,
  "symbols": null,                       // Optional
  "timeframe": "1d",                     // Optional
  "period": "6mo",                       // Optional
  "top_n": 10,                           // Optional
  "step_size": 1                         // Optional
}

Response:
{
  "success": true,
  "message": "Found 10 matching patterns",
  "matches": [...],
  "pattern_stats": {...},
  "search_params": {...}
}
```

## Troubleshooting

### "Error searching for patterns"
**Cause:** Backend API not running or unreachable
**Solution:** Ensure API is running at `http://localhost:8000`

```bash
cd api
uvicorn main:app --reload
```

### "Pattern has insufficient variation"
**Cause:** Pattern is too flat (all values similar)
**Solution:** Draw a pattern with more ups and downs

### No matches found
**Cause:** Pattern is too specific or unusual
**Solution:**
- Try a simpler, more common pattern
- Increase search period (modify request)
- Search more symbols

### Slow search
**Cause:** Searching many stocks with high resolution
**Solution:**
- Reduce number of points (e.g., 30 instead of 50)
- Backend will cache stock data for faster subsequent searches

### Canvas not working on mobile
**Cause:** Browser touch events not properly handled
**Solution:** Already implemented touch handlers - if issues persist, try:
- Use latest browser version
- Ensure JavaScript is enabled
- Try different browser

## Future Enhancements

Planned features:
- [ ] Custom symbol selection
- [ ] Different timeframes (weekly, monthly)
- [ ] Pattern library (save/load patterns)
- [ ] Share patterns via URL
- [ ] Export results to CSV
- [ ] Advanced filters (sector, market cap)
- [ ] Real-time pattern alerts
- [ ] Pattern overlay on stock charts

## Files

**Components:**
- `/components/PatternCanvas.tsx` - Main drawing canvas
- `/components/PatternResults.tsx` - Results display

**Utils:**
- `/lib/canvas-utils.ts` - Pattern simplification & normalization

**Pages:**
- `/app/draw/page.tsx` - Drawing page route

**Layout:**
- `/app/layout.tsx` - Navigation (includes "Draw Pattern" link)