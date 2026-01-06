# Trader Alpha API

FastAPI service for generating stock charts on demand.

## Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Run Locally

```bash
source venv/bin/activate
uvicorn main:app --reload --port 8000
```

## Endpoints

- `GET /` - API info
- `GET /health` - Health check
- `GET /chart/{symbol}` - Generate chart for a stock symbol

## Example

```bash
# Open in browser
open http://localhost:8000/chart/AAPL
```

## Deploy to Railway

1. Create a new project on Railway
2. Connect your GitHub repository
3. Set the root directory to `/api`
4. Railway will auto-detect FastAPI and deploy
