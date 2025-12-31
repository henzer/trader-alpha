# Data Provider

Módulo para obtener datos históricos OHLCV de stocks con sistema de cache integrado.

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
from src import YFinanceProvider, Timeframe

# Crear provider con cache habilitado
provider = YFinanceProvider(use_cache=True)

# Obtener datos de un stock
df_weekly = provider.get_stock_data("AAPL", Timeframe.WEEKLY, period="2y")
df_monthly = provider.get_stock_data("AAPL", Timeframe.MONTHLY, period="5y")

# Obtener múltiples stocks
symbols = ["AAPL", "MSFT", "GOOGL"]
data = provider.get_multiple_stocks(symbols, Timeframe.WEEKLY, period="2y")

# Limpiar cache
provider.clear_old_cache(days=7)  # Elimina cache > 7 días
provider.clear_cache()            # Elimina todo el cache
```

## Estructura

- `src/models/` - Modelos Pydantic (Timeframe, requests)
- `src/providers/` - Implementación de data providers
  - `base.py` - Clase abstracta base
  - `yfinance_provider.py` - Implementación con yfinance
- `src/cache/` - Sistema de cache file-based
- `tests/` - Tests unitarios

## Sistema de Cache

### Ubicación
Cache se guarda en `~/.trader-alpha/cache/`

### Formato de archivos
```
AAPL_1wk_2y_20231221.parquet
{symbol}_{timeframe}_{period}_{date}.parquet
```

### TTL (Time To Live)
- **Daily**: 6 horas
- **Weekly**: 24 horas
- **Monthly**: 72 horas

### Ventajas
- Evita rate limiting de APIs
- Reduce tiempo de respuesta
- Persiste entre sesiones
- Formato eficiente (parquet)

## Providers disponibles

### YFinanceProvider
- **API**: Yahoo Finance (gratis)
- **Rate limits**: ~2000 requests/hour
- **Datos**: Históricos, delayed
- **Requiere API key**: No

## Timeframes soportados

- `Timeframe.DAILY` - Datos diarios (1d)
- `Timeframe.WEEKLY` - Datos semanales (1wk)
- `Timeframe.MONTHLY` - Datos mensuales (1mo)

## Períodos soportados

Ejemplos: `"1d"`, `"5d"`, `"1mo"`, `"3mo"`, `"6mo"`, `"1y"`, `"2y"`, `"5y"`, `"10y"`, `"ytd"`, `"max"`