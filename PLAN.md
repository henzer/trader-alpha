# Trader Alpha - Plan de Implementación

## Visión General del Sistema

Sistema modular para evaluar oportunidades de entrada en largo (long positions) en stocks.

### Módulos del Sistema Completo
1. **score-engine**: Motor de calificación/puntuación (FASE ACTUAL)
2. **data-provider**: Obtención de datos de APIs públicas
3. **graph**: Visualización de stocks
4. **trader-alpha**: Módulo integrador que combina los 3 anteriores y rankea stocks

---

## FASE 1: score-engine (Actual)

### Objetivo
Crear motor de puntuación para evaluar el momento óptimo de entrada en largo en un stock.

### Arquitectura del score-engine

#### 1. Filtro Inicial (Obligatorio)
**Monthly BX-Trender - Macro Uptrend Detection**
- **Propósito**: Determinar si estamos en macro uptrend
- **Lógica**:
  - ✅ PASA: Rojo claro, Verde claro, o Verde intenso
  - ❌ DESCARTA: Rojo intenso
- **Acción**: Si no pasa → puntuación = 0 (descartar stock)

#### 2. Indicadores de Puntuación (Solo si pasa filtro)

##### 2.1 Market Bias (Timeframes: Weekly, Monthly, 6-Month)
**Propósito**: Evaluar si el precio actual está en fair price/descuento

**Puntuación**:
- Weekly Market Bias: 3 pts
- Monthly Market Bias: 6 pts
- 6-Month Market Bias: 9 pts

**Lógica**: 
- NO es acumulativo
- Se toma el mayor puntaje
- Mayor timeframe = mayor descuento = mejor oportunidad

**Implementación**:
- Código base: PineScript (pendiente recibir)
- Traducir a Python/TypeScript

##### 2.2 Fibonacci Retracement
**Propósito**: Identificar si estamos en zona de Smart Money (acumulación/descuento)

**Zonas clave**:
- 0.618 - 0.786 (Golden Pocket - zona premium de compra)
- Puntuación pendiente definir

**Implementación**:
- Código base: PineScript (pendiente recibir)
- Traducir a Python/TypeScript

---

### Estructura del score-engine

```
score-engine/
├── src/
│   ├── filters/
│   │   └── bx_trender_filter.py       # Filtro macro uptrend
│   ├── indicators/
│   │   ├── bx_trender.py              # Implementación BX-Trender
│   │   ├── market_bias.py             # Implementación Market Bias
│   │   └── fibonacci_retracement.py   # Implementación Fibonacci
│   ├── scoring/
│   │   ├── market_bias_scorer.py      # Puntuación Market Bias
│   │   ├── fibonacci_scorer.py        # Puntuación Fibonacci
│   │   └── total_score.py             # Calculador de puntuación total
│   ├── types/
│   │   └── __init__.py                # Tipos y clases base
│   └── __init__.py                    # Entry point
├── tests/
│   └── ...
├── requirements.txt
├── setup.py
└── README.md
```

---

### Flujo de Puntuación

```
1. Input: Stock data (OHLCV + timeframes)
   ↓
2. Filtro Inicial: Monthly BX-Trender
   ↓
   ├─ Rojo intenso? → Score = 0 (DESCARTADO)
   ├─ Rojo claro/Verde claro/Verde intenso? → Continuar
   ↓
3. Calcular indicadores:
   ├─ Market Bias (weekly, monthly, 6-month)
   ├─ Fibonacci Retracement
   ↓
4. Scoring:
   ├─ Market Bias score (max 9 pts)
   ├─ Fibonacci score (pendiente definir)
   ↓
5. Output: Total Score + desglose
```

---

### Tareas Pendientes

#### Fase 1A: Setup & Estructura
- [ ] Crear estructura de carpetas del score-engine
- [ ] Configurar entorno Python (requirements.txt, setup.py)
- [ ] Definir clases base y Pydantic models

#### Fase 1B: Implementación de Indicadores
- [ ] Recibir código PineScript de Market Bias
- [ ] Recibir código PineScript de BX-Trender
- [ ] Recibir código PineScript de Fibonacci Retracement (opcional)
- [ ] Traducir Market Bias a código
- [ ] Traducir BX-Trender a código
- [ ] Traducir Fibonacci Retracement a código

#### Fase 1C: Sistema de Filtrado
- [ ] Implementar filtro Monthly BX-Trender
- [ ] Tests del filtro

#### Fase 1D: Sistema de Puntuación
- [ ] Implementar scorer de Market Bias
- [ ] Definir y implementar scorer de Fibonacci
- [ ] Implementar calculador de puntuación total
- [ ] Tests de puntuación

#### Fase 1E: Integración
- [ ] Crear API/interfaz del score-engine
- [ ] Tests de integración
- [ ] Documentación

---

### Stack Tecnológico Definido

#### Backend (Core Logic)
- **Lenguaje**: Python 3.11+
- **Framework API**: FastAPI (para futuro endpoint REST)
- **Librerías principales**:
  - `pandas`: Manipulación de datos financieros
  - `numpy`: Cálculos numéricos
  - `pandas-ta` / `ta-lib`: Indicadores técnicos
  - `yfinance` / `alpaca-py`: Data providers (módulo data-provider)
  - `pytest`: Testing
  - `pydantic`: Validación de datos y tipos

#### Frontend (Futuro - Fase 4)
- **Framework**: Next.js (TypeScript)
- **UI**: React + TailwindCSS
- **Charts**: Plotly.js / Lightweight Charts
- **Comunicación**: REST API (consume backend Python)

#### Ventajas de este stack:
- Python: Ecosistema financiero maduro y eficiente
- Separación clara: Backend (Python) ↔ Frontend (Next.js)
- Escalable: FastAPI permite agregar endpoints fácilmente
- Flexible: score-engine puede usarse standalone o via API

---

### Decisiones Técnicas Pendientes

1. ✅ **Lenguaje**: Python (backend) + Next.js (frontend futuro)
2. **Fibonacci**: ¿Puntuación y zonas exactas?
3. **Data format**: DataFrame de pandas (OHLCV estándar)
4. **Output format**: Pydantic models con score + breakdown

---

### Notas de Implementación

- Los indicadores originales están en PineScript (TradingView)
- Traducir lógica PineScript → Python usando pandas/numpy
- Priorizar código limpio y modular
- Cada indicador debe ser testeable independientemente
- El score-engine debe ser agnóstico del data-provider
- Usar type hints de Python para mejor mantenibilidad
- Documentación con docstrings (Google style)

---

## Próximos Pasos

1. Recibir códigos PineScript de indicadores
2. ✅ Stack tecnológico definido (Python)
3. Definir puntuación de Fibonacci
4. Crear estructura base del proyecto Python
5. Iniciar implementación del score-engine