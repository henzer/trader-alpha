# Stock Lists

Este directorio contiene archivos CSV con listas de stocks para escanear.

## Formato de CSV

Cada archivo CSV debe tener el siguiente formato:

```csv
symbol
AAPL
MSFT
NVDA
```

- **Columna requerida**: `symbol`
- Una acción por línea
- El nombre del archivo (sin extensión) se usa como `list_name` en la base de datos

## Listas Disponibles

### Índices
- **SP500.csv**: S&P 500 (~500 stocks)
- **NASDAQ100.csv**: NASDAQ 100 (~100 stocks)
- **RUSSELL1000.csv**: Russell 1000 Growth (~100 stocks)

### Temáticas
- **Growth.csv**: Stocks de crecimiento (Tech, Cloud, etc)
- **Fintech.csv**: Fintech & Payments

## Agregar Nueva Lista

1. Crear archivo CSV en este directorio (ej: `MyList.csv`)
2. Agregar columna `symbol` con los tickers
3. El scanner automáticamente la detectará en el próximo run

## Notas

- Un stock puede estar en múltiples listas
- El campo `list_name` en la BD guardará todas las listas separadas por coma (ej: "SP500, Growth")
- CSVs inválidos serán ignorados con un warning