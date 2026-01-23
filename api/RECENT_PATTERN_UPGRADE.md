# Recent Pattern Matching - Upgrade Notes

## What Changed?

The pattern matching algorithm has been upgraded to focus on **patterns forming NOW**, not historical patterns.

## Before (Old Behavior)

```python
# Searched ENTIRE history (6 months)
# Could match patterns from 3-4 months ago
# Not useful for current trading decisions
```

**Example Problem:**
- You draw an uptrend pattern
- Algorithm finds the best match from 3 months ago
- But that stock is currently in a downtrend
- **Result:** Misleading, not actionable

## After (New Behavior - Default)

```python
# Searches ONLY patterns ending in the last 3 days
# Tries multiple window sizes (30, 40, 50, 60, 70 days)
# All matches end at "today"
```

**Example Solution:**
- You draw an uptrend pattern
- Algorithm finds stocks with uptrends ending TODAY
- You see what's happening NOW
- **Result:** Actionable trading signals

## Key Changes

### 1. New Function: `find_recent_pattern_match()`

Located in `utils/dtw_matcher.py`

```python
def find_recent_pattern_match(
    pattern: np.ndarray,
    df: pd.DataFrame,
    window_sizes: List[int],      # NEW: Try multiple durations
    max_days_ago: int = 3,         # NEW: How "recent" is recent
    radius: int = 10
) -> Optional[Tuple[int, int, float, int]]:
```

**What it does:**
1. Takes your drawn pattern
2. Tries windows of different sizes (e.g., 30, 40, 50, 60 days)
3. All windows MUST end within the last 3 days
4. Returns the best match (lowest DTW distance)

### 2. Updated Function: `match_pattern_to_stock()`

**New Parameters:**
- `recent_only: bool = True` - Enable recent-only mode (default)
- `window_size_range: Optional[List[int]] = None` - Window sizes to try

**Default window sizes:**
```python
base_size = len(pattern)  # e.g., 50
window_size_range = [
    base_size - 20,  # 30 days
    base_size - 10,  # 40 days
    base_size,       # 50 days
    base_size + 10,  # 60 days
    base_size + 20   # 70 days
]
```

### 3. Updated Endpoint: `POST /pattern/match`

Now includes in response:
```json
{
  "search_params": {
    "search_mode": "recent_only",
    "window_size_range": [30, 40, 50, 60, 70, 80]
  }
}
```

## Why Multiple Window Sizes?

Your drawn pattern represents a price movement, but you don't know the exact duration:

- **30 days?** Sharp, quick movement
- **50 days?** Moderate pace
- **70 days?** Slow, gradual movement

The algorithm tests all reasonable durations and picks the best match.

## Technical Details

### Algorithm Flow (Recent Mode)

```
1. Fetch 6 months of daily data for stock
   └─> 180 data points

2. For each window size in [30, 40, 50, 60, 70]:
   └─> For end_offset in [0, 1, 2, 3]:
       └─> Extract window: prices[start:end]
           where end = last_index - end_offset
       └─> Resize pattern to match window size
       └─> Calculate DTW(pattern, window)
       └─> Track best match (lowest distance)

3. Return best match across all window sizes
   └─> This match ENDS within last 3 days
```

### Pattern Resizing

Since window sizes vary (30-70 days) but your pattern is fixed (e.g., 50 points), we resize:

```python
# Linear interpolation to resize pattern
if len(pattern) != window_size:
    old_indices = np.linspace(0, len(pattern) - 1, len(pattern))
    new_indices = np.linspace(0, len(pattern) - 1, window_size)
    resized_pattern = np.interp(new_indices, old_indices, pattern)
```

This preserves the shape while changing duration.

## Performance Impact

**Faster than before!**

- **Before:** Searched ~150 windows (entire history with step_size=1)
- **After:** Searches ~20-25 windows (5 sizes × 4 end positions)

**Result:** 6x faster while being MORE relevant!

## Example Results

### Before (Historical Mode)
```
Match 1: AAPL
  Date Range: 2024-03-15 to 2024-05-15
  Similarity: 92%
  Status: Pattern from 5 months ago ❌
```

### After (Recent Mode)
```
Match 1: AAPL
  Date Range: 2024-11-01 to 2024-12-20
  Similarity: 88%
  Status: Pattern forming NOW ✅
```

## Migration Guide

### For API Users

**No changes required!** Recent mode is now the default.

If you want the old behavior (search entire history):
```python
# Backend: Set recent_only=False
matches = match_pattern_to_multiple_stocks(
    pattern=pattern,
    symbols=symbols,
    dfs=dfs,
    recent_only=False  # Search entire history
)
```

### For Frontend

**No changes required!** The frontend automatically benefits from the new algorithm.

Optional: Add UI toggle for "Recent" vs "Historical" mode in future.

## Testing

Test the new behavior:

```bash
cd api
python test_pattern_endpoint.py
```

The test will show:
- Date ranges of matches
- All should end within last 3 days
- Different window sizes tried

## FAQ

**Q: What if I want to search historical patterns?**
A: Set `recent_only=False` in the function call.

**Q: Can I change the "3 days ago" limit?**
A: Yes, modify `max_days_ago` parameter in `find_recent_pattern_match()`.

**Q: Why not just use the exact pattern length?**
A: Because your drawn pattern might represent different time durations. Testing multiple sizes finds the best temporal match.

**Q: What if no patterns are found?**
A: Try:
- Drawing a simpler pattern
- Increasing `max_days_ago` to 7
- Searching more symbols
- Using a different timeframe (weekly instead of daily)

## Benefits

1. ✅ **Actionable Signals** - See what's happening NOW
2. ✅ **Faster** - Search fewer windows
3. ✅ **Flexible Duration** - Auto-adjusts for pattern timing
4. ✅ **Better Matches** - Focus on recent data improves relevance
5. ✅ **Trading Ready** - All matches are current, not historical

## Rollback Plan

If you need to revert to old behavior:

```python
# In main.py, change:
recent_only=True  # Change to False

# And remove:
window_size_range=window_size_range  # Remove this parameter
```

This will restore the old "search entire history" behavior.