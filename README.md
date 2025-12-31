# Trader Alpha 📈

Sistema modular para evaluar oportunidades de entrada en largo (long positions) en stocks con análisis técnico automatizado.

## 🏗️ Arquitectura del Monorepo

```
trader-alpha/
├── data-provider/         # Obtención de datos históricos (yfinance + cache)
├── score-engine/          # Motor de puntuación técnica
├── graph/                 # Visualización con Plotly
├── scanner/               # Scanner diario automatizado
├── webapp/               # Frontend Next.js (próximamente)
└── .github/workflows/    # GitHub Actions para scan automático
```

## 📦 Módulos

### 1. **data-provider**
Obtiene datos históricos de stocks con sistema de cache inteligente.
- Provider: yfinance
- Cache TTL: 6h (daily), 24h (weekly), 72h (monthly)
- Timeframes: Daily, Weekly, Monthly

### 2. **score-engine**
Motor de análisis técnico que calcula puntuación de 0-11 pts.

**Filtro inicial:**
- Monthly BX-Trender (descarta downtrends)

**Indicadores:**
- Market Bias (0-6 pts): Zonas de valor Heikin Ashi
- Fibonacci Retracement (0-5 pts): Golden/Smart Money Zones

### 3. **graph**
Visualización interactiva con Plotly.
- Candlesticks con Market Bias zones
- BX-Trender multi-timeframe
- Fibonacci con TP/SL automáticos
- Score annotation

### 4. **scanner**
Scanner diario automatizado vía GitHub Actions.
- Analiza ~200+ stocks (QQQ, SPY, IWF)
- Procesamiento paralelo (10 workers)
- Almacena en Supabase
- Corre Lun-Vie 9PM UTC

## 🚀 Quick Start

### Instalación

```bash
# Clonar repo
git clone <repo-url>
cd trader-alpha

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### Uso

#### Analizar un stock individual

```bash
source venv/bin/activate
python examples/test_graph.py AAPL
```

#### Analizar múltiples stocks

```bash
python examples/analyze_multiple_stocks.py
```

#### Scanner diario (local)

```bash
cd scanner
cp .env.example .env
# Editar .env con credenciales de Supabase
cd src
python daily_scan.py
```

## 📊 Sistema de Puntuación

### Filtro Macro Uptrend
- **Monthly BX-Trender** > 0 (verde)
- Si falla: stock se marca como "FAIL" pero se calcula score

### Scoring (0-11 pts)

| Indicador | Condición | Puntos |
|-----------|-----------|--------|
| Market Bias | Monthly (precio en zona) | 6 pts |
| Market Bias | Weekly (precio en zona) | 3 pts |
| Fibonacci | Golden Zone (0.786-0.826) | 5 pts |
| Fibonacci | Smart Money Zone (0.618-0.786) | 3 pts |

**Ejemplo:**
```
VITL: 11/11 pts (FAIL filter)
  ├─ Market Bias: 6 pts (Monthly)
  ├─ Fibonacci: 5 pts (Golden Zone)
  └─ BX-Trender: RED (downtrend)
```

## 🤖 Automatización con GitHub Actions

### Setup

1. **Crear proyecto Supabase:**
   ```bash
   # Ejecutar SQL en Supabase SQL Editor
   cat scanner/supabase_schema.sql
   ```

2. **Configurar GitHub Secrets:**
   ```
   Settings → Secrets → Actions → New secret
   
   SUPABASE_URL=https://xxx.supabase.co
   SUPABASE_KEY=eyJhbGc...
   ```

3. **Trigger automático:**
   - Corre Lun-Vie 9PM UTC (después del cierre)
   - O manualmente desde Actions tab

### Workflow

```
GitHub Action → Analiza ~200 stocks → Supabase
     ↓
webapp (Next.js) lee top 50 → Usuario click stock → Genera gráfica
```

## 🗄️ Base de Datos (Supabase)

### Tabla: `stock_scores`

```sql
symbol, scan_date, score, passed_filter, 
market_bias_score, fibonacci_score, 
bx_color, swing_high, swing_low
```

### Queries útiles

```python
from scanner.src.supabase_client import SupabaseClient

client = SupabaseClient()

# Top 50 del último scan
top_stocks = client.get_top_stocks(limit=50)

# Historial de un stock
history = client.get_stock_history("AAPL", days=30)
```

## 📁 Estructura Detallada

```
trader-alpha/
├── data-provider/
│   └── src/
│       ├── providers/yfinance_provider.py
│       ├── cache/cache_manager.py
│       └── models/__init__.py
├── score-engine/
│   └── src/
│       ├── filters/bx_trender_filter.py
│       ├── indicators/
│       │   ├── bx_trender.py
│       │   ├── market_bias.py
│       │   └── fibonacci_retracement.py
│       ├── scoring/
│       │   ├── market_bias_scorer.py
│       │   ├── fibonacci_scorer.py
│       │   └── total_score.py
│       └── types/__init__.py
├── graph/
│   └── src/
│       ├── stock_chart.py
│       └── charts/
├── scanner/
│   ├── src/
│   │   ├── daily_scan.py
│   │   ├── stock_analyzer.py
│   │   ├── supabase_client.py
│   │   └── index_fetcher.py
│   └── supabase_schema.sql
├── examples/
│   ├── test_graph.py
│   └── analyze_multiple_stocks.py
├── .github/workflows/
│   └── daily-scan.yml
└── requirements.txt
```

## 🔧 Configuración

### Cache
- Ubicación: `~/.trader-alpha/cache/`
- Formato: Parquet
- TTL configurable por timeframe

### Environment Variables
```bash
# scanner/.env
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJhbGc...
```

## 📝 Ejemplos de Output

### Terminal
```
✅ AAPL: Score=9/11, Filter=PASS
✅ MSFT: Score=6/11, Filter=FAIL
✅ GOOGL: Score=11/11, Filter=PASS
```

### Gráfica HTML
- Candlesticks con zonas Market Bias (verde/azul)
- BX-Trender bars (monthly/weekly)
- Fibonacci levels + TP/SL lines
- Score annotation (bottom-left)

## 🚧 Próximos Pasos

- [ ] webapp con Next.js + Tailwind
- [ ] API FastAPI para gráficas on-demand
- [ ] Deploy en Vercel + Railway
- [ ] Dashboard con top 50 stocks
- [ ] Alertas via Telegram/Email
- [ ] Backtesting module

## 📄 Licencia

MIT

---

**Desarrollado con Python, Plotly, Next.js y Supabase**