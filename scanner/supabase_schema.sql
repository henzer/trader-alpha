-- Stock Scores Table
CREATE TABLE IF NOT EXISTS stock_scores (
  id BIGSERIAL PRIMARY KEY,
  symbol TEXT NOT NULL,
  scan_date DATE NOT NULL,
  score INTEGER NOT NULL,
  passed_filter BOOLEAN NOT NULL DEFAULT FALSE,
  market_bias_score INTEGER,
  market_bias_timeframe TEXT,
  fibonacci_score INTEGER,
  fibonacci_zone TEXT,
  bx_color TEXT,
  swing_high DECIMAL(10, 2),
  swing_low DECIMAL(10, 2),
  current_price DECIMAL(10, 2),
  list_name TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(symbol, scan_date)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_stock_scores_scan_date ON stock_scores(scan_date DESC);
CREATE INDEX IF NOT EXISTS idx_stock_scores_score ON stock_scores(score DESC);
CREATE INDEX IF NOT EXISTS idx_stock_scores_symbol ON stock_scores(symbol);
CREATE INDEX IF NOT EXISTS idx_stock_scores_composite ON stock_scores(scan_date DESC, score DESC);
CREATE INDEX IF NOT EXISTS idx_stock_scores_list_name ON stock_scores(list_name);

-- RLS (Row Level Security) - optional, enable if needed
ALTER TABLE stock_scores ENABLE ROW LEVEL SECURITY;

-- Policy to allow anonymous read access
CREATE POLICY "Allow public read access" ON stock_scores
  FOR SELECT USING (true);

-- Policy to allow service role to insert/update
CREATE POLICY "Allow service role all access" ON stock_scores
  FOR ALL USING (true);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger to auto-update updated_at
CREATE TRIGGER update_stock_scores_updated_at
  BEFORE UPDATE ON stock_scores
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- View for latest scan results
CREATE OR REPLACE VIEW latest_stock_scores AS
SELECT DISTINCT ON (symbol)
  *
FROM stock_scores
ORDER BY symbol, scan_date DESC;

-- View for top stocks from latest scan
CREATE OR REPLACE VIEW top_stocks_latest AS
SELECT *
FROM stock_scores
WHERE scan_date = (SELECT MAX(scan_date) FROM stock_scores)
ORDER BY score DESC
LIMIT 50;