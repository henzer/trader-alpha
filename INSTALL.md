# Installation Guide

## Local Development Setup

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/trader-alpha.git
cd trader-alpha
```

### 2. Install Python packages

```bash
# Install all modules in editable mode
pip install -e ./data-provider
pip install -e ./score-engine
pip install -e ./graph
pip install -r scanner/requirements.txt
```

### 3. Configure environment

```bash
cd scanner
cp .env.example .env
# Edit .env with your Supabase credentials
```

### 4. Test locally

```bash
# Test score engine
python main.py AAPL MSFT NVDA

# Test with graphs
python examples/test_graph.py AAPL

# Run scanner locally
cd scanner/src
python daily_scan.py
```

## GitHub Actions Setup

### 1. Push to GitHub

```bash
git add .
git commit -m "Initial commit"
git push
```

### 2. Configure Secrets

1. Go to repository Settings → Secrets and variables → Actions
2. Add repository secrets:
   - `SUPABASE_URL`: Your Supabase project URL
   - `SUPABASE_KEY`: Your Supabase anon/public key

### 3. Verify workflow

- Go to Actions tab
- Run "Daily Stock Scanner" manually
- Check logs for errors

## Troubleshooting

### Import errors

If you see `ModuleNotFoundError: No module named 'src'`:

```bash
# Reinstall packages in editable mode
pip install -e ./data-provider
pip install -e ./score-engine
pip install -e ./graph
```

### GitHub Actions fails

Check that:
1. Secrets are configured correctly
2. All requirements.txt files are up to date
3. Python version is 3.11 in workflow file