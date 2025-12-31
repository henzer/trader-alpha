# Scanner Module

Automated daily stock scanner that analyzes stocks from custom CSV lists and stores results in Supabase.

## Setup

### 1. Quick Setup (Recommended)

```bash
cd scanner
./setup.sh
```

This will:
- Create a virtual environment
- Install all dependencies
- Create `.env` template

### 2. Manual Setup

```bash
cd scanner
python3 -m venv venv
source venv/bin/activate
pip install -r ../requirements.txt
pip install -r requirements.txt
```

### 2. Configure Stock Lists

Stock lists are defined in CSV files in the `lists/` directory.

**Available lists:**
- `SP500.csv` - S&P 500 stocks
- `NASDAQ100.csv` - NASDAQ 100 stocks
- `RUSSELL1000.csv` - Russell 1000 Growth
- `Growth.csv` - Growth stocks (Tech, Cloud, etc)
- `Fintech.csv` - Fintech & Payments

**To create a new list:**
1. Create a CSV file in `lists/` (e.g., `MyList.csv`)
2. Add a `symbol` column with stock tickers:
   ```csv
   symbol
   AAPL
   MSFT
   NVDA
   ```
3. The scanner will automatically detect it

See `lists/README.md` for more details.

### 3. Configure Supabase

1. Create a Supabase project at https://supabase.com
2. Run the SQL schema in the Supabase SQL Editor:
   ```bash
   cat supabase_schema.sql
   ```
3. Get your project credentials:
   - Go to Project Settings → API
   - Copy `URL` and `anon/public` key

### 4. Set Environment Variables

Create a `.env` file in the `scanner/` directory:

```bash
cp .env.example .env
```

Edit `.env` and add your Supabase credentials:

```
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 5. Test Locally

```bash
cd scanner/src
python daily_scan.py
```

## GitHub Actions Setup

### Configure Secrets

1. Go to your GitHub repository
2. Settings → Secrets and variables → Actions
3. Add the following secrets:
   - `SUPABASE_URL`: Your Supabase project URL
   - `SUPABASE_KEY`: Your Supabase anon/public key

### Schedule

The GitHub Action runs automatically:
- **Schedule**: Monday-Friday at 9:00 PM UTC (4:00 PM EST - after market close)
- **Manual**: Can be triggered manually from the Actions tab

## Architecture

```
scanner/
├── lists/
│   ├── SP500.csv              # S&P 500 stocks
│   ├── NASDAQ100.csv          # NASDAQ 100 stocks
│   ├── RUSSELL1000.csv        # Russell 1000 Growth
│   ├── Growth.csv             # Growth stocks
│   ├── Fintech.csv            # Fintech stocks
│   └── README.md              # List format documentation
├── src/
│   ├── list_fetcher.py        # Reads symbols from CSV lists
│   ├── stock_analyzer.py      # Analyzes individual stocks
│   ├── supabase_client.py     # Supabase database client
│   └── daily_scan.py          # Main scan orchestrator
├── supabase_schema.sql        # Database schema
├── requirements.txt           # Python dependencies
└── .env.example               # Environment template
```

## Features

- ✅ **CSV-based lists**: Define custom stock lists in simple CSV files
- ✅ **Multi-list support**: Stocks can belong to multiple lists
- ✅ **Parallel processing**: 10 concurrent workers
- ✅ **Fast scanning**: Analyzes ~200+ stocks in ~5-10 minutes
- ✅ **Supabase storage**: Stores daily scores with list metadata
- ✅ **GitHub Actions**: Automated daily scans
- ✅ **Top 50 view**: Easy query for best opportunities
- ✅ **Historical tracking**: Track score evolution over time

## Data Collected

For each stock:
- Total score (0-11)
- Filter pass/fail status
- Market Bias score & timeframe
- Fibonacci score & zone
- BX-Trender color
- Swing high/low levels
- **List membership** (which lists the stock belongs to)
- Scan date & timestamp

## Querying Data

### Get Top 50 Stocks from Latest Scan

```python
from supabase_client import SupabaseClient

client = SupabaseClient()
top_stocks = client.get_top_stocks(limit=50)
```

### Get Stock History

```python
history = client.get_stock_history("AAPL", days=30)
```

### Using Supabase Views

```sql
-- Latest scores for all stocks
SELECT * FROM latest_stock_scores;

-- Top 50 from latest scan
SELECT * FROM top_stocks_latest;
```