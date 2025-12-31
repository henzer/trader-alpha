# Score Engine

Motor de puntuación para evaluar oportunidades de entrada en largo (long positions) en stocks.

## Instalación

### 1. Crear y activar entorno virtual

```bash
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

## Uso básico

```python
import pandas as pd
from src import calculate_stock_score

# Cargar datos (OHLCV)
df_monthly = pd.DataFrame({
    'close': [...],
    'open': [...],
    'high': [...],
    'low': [...],
    'volume': [...]
})

df_weekly = pd.DataFrame({
    'close': [...],
    'open': [...],
    'high': [...],
    'low': [...],
    'volume': [...]
})

# Calcular puntuación del stock
score = calculate_stock_score(
    symbol="AAPL",
    df_monthly=df_monthly,
    df_weekly=df_weekly
)

print(f"Symbol: {score.symbol}")
print(f"Total Score: {score.score_breakdown.total_score}")
print(f"Passed Filter: {score.score_breakdown.passed_filter}")
print(f"Market Bias Score: {score.score_breakdown.market_bias_score}")
print(f"Market Bias Timeframe: {score.score_breakdown.market_bias_timeframe}")
```

## Estructura

- `src/types/` - Modelos Pydantic y enums
- `src/indicators/` - Implementación de indicadores técnicos
- `src/filters/` - Filtros de screening
- `src/scoring/` - Sistema de puntuación (WIP)
- `tests/` - Tests unitarios
- `venv/` - Entorno virtual Python

## Indicadores implementados

- [x] BX-Trender (filtro macro uptrend)
- [x] Market Bias (puntuación por timeframe: Weekly=3pts, Monthly=6pts)
- [x] Fibonacci Retracement (puntuación zona Smart Money)

## Sistema de puntuación

### Filtro inicial
1. **Monthly BX-Trender**: Descarta stocks en downtrend (color rojo oscuro)

### Scoring (si pasa filtro)
1. **Market Bias**:
   - Monthly (en rango): 6 pts
   - Weekly (en rango): 3 pts
   - Fuera de rango: 0 pts
   
2. **Fibonacci Retracement**:
   - Golden Zone (0.786-0.826): 5 pts
   - Smart Money Zone (0.618-0.786): 3 pts
   - Fuera de zona: 0 pts

**Puntuación máxima**: 11 pts (6 Market Bias + 5 Fibonacci)

## Configuración

- **Market Bias**: period=20, smoothing=7
- **BX-Trender**: short_l1=5, short_l2=20, short_l3=15
- **Fibonacci**: lookback=10 (configurable para detección de pivots)