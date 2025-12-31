# Graph Module

Módulo para generar gráficos interactivos de stocks con indicadores técnicos usando Plotly.

## Instalación

```bash
pip install -r requirements.txt
```

## Uso básico

```python
from src import StockChart
import pandas as pd

# Crear gráfico base
chart = StockChart(symbol="AAPL", df=df_weekly)
chart.create_base_chart(with_bx_trender=True)

# Agregar indicadores
chart.add_market_bias(bias_high, bias_low, name="Weekly Market Bias")
chart.add_fibonacci(swing_high=150.0, swing_low=120.0)
chart.add_bx_trender(bx_values)

# Guardar como HTML
output_path = chart.save()  # Guarda en output/AAPL_chart.html
print(f"Chart saved to: {output_path}")

# O mostrar en navegador
chart.show()
```

## Características

### Gráfico de Candlestick
- Velas japonesas (OHLC)
- Colores: Verde (alcista), Rojo (bajista)
- Tema oscuro profesional
- Interactivo (zoom, pan, hover)

### Indicadores soportados

#### 1. Market Bias
- Zona sombreada verde
- Muestra rango de "fair price"
- Soporta múltiples timeframes

#### 2. Fibonacci Retracement
- Niveles clave: 0.618, 0.786, 0.826
- Golden Zone destacada (0.786-0.826)
- Opción de mostrar todos los niveles

#### 3. BX-Trender
- Subpanel con histograma
- Colores:
  - Verde claro: Positivo y subiendo
  - Verde oscuro: Positivo y bajando
  - Rojo claro: Negativo y subiendo
  - Rojo oscuro: Negativo y bajando

## Estructura

```
graph/
├── src/
│   ├── charts/
│   │   ├── candlestick.py    # Gráfico base
│   │   └── indicators.py      # Indicadores
│   ├── stock_chart.py         # Clase principal
│   └── __init__.py
├── output/                    # HTML generados
├── requirements.txt
└── README.md
```

## Output

Los gráficos se guardan como archivos HTML interactivos que se pueden:
- Abrir directamente en el navegador
- Compartir por email/Slack
- Embeber en sitios web
- Exportar como imágenes (PNG, SVG)

## Ejemplo completo

Ver `examples/test_graph.py` para un ejemplo de uso con integración completa con score-engine y data-provider.
