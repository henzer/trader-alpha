import plotly.graph_objects as go
import pandas as pd
import numpy as np
from typing import Tuple, Optional


def add_market_bias(
    fig: go.Figure,
    df: pd.DataFrame,
    bias_high: pd.Series,
    bias_low: pd.Series,
    name: str = "Market Bias"
) -> go.Figure:
    fig.add_trace(go.Scatter(
        x=df.index,
        y=bias_high,
        mode='lines',
        name=f'{name} High',
        line=dict(color='rgba(0, 255, 0, 0)', width=0),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    fig.add_trace(go.Scatter(
        x=df.index,
        y=bias_low,
        mode='lines',
        name=name,
        line=dict(color='rgba(0, 255, 0, 0)', width=0),
        fill='tonexty',
        fillcolor='rgba(0, 255, 0, 0.1)',
        showlegend=True,
        hovertemplate=f'{name}<br>High: %{{y:.2f}}<extra></extra>'
    ))
    
    return fig


def add_fibonacci_levels(
    fig: go.Figure,
    swing_high: float,
    swing_low: float,
    start_date: pd.Timestamp,
    end_date: pd.Timestamp,
    show_all_levels: bool = False
) -> go.Figure:
    diff = swing_high - swing_low
    
    levels = {
        '0.0': swing_high,
        '0.236': swing_high - (diff * 0.236),
        '0.382': swing_high - (diff * 0.382),
        '0.5': swing_high - (diff * 0.5),
        '0.618': swing_high - (diff * 0.618),
        '0.786': swing_high - (diff * 0.786),
        '0.826': swing_high - (diff * 0.826),
        '1.0': swing_low
    }
    
    key_levels = ['0.618', '0.786', '0.826'] if not show_all_levels else levels.keys()
    
    colors = {
        '0.0': 'rgba(255, 255, 255, 0.3)',
        '0.236': 'rgba(128, 128, 128, 0.3)',
        '0.382': 'rgba(128, 128, 128, 0.3)',
        '0.5': 'rgba(255, 255, 0, 0.3)',
        '0.618': 'rgba(0, 255, 255, 0.5)',
        '0.786': 'rgba(255, 215, 0, 0.5)',
        '0.826': 'rgba(255, 165, 0, 0.5)',
        '1.0': 'rgba(255, 255, 255, 0.3)'
    }
    
    for level_name in key_levels:
        price = levels[level_name]
        color = colors.get(level_name, 'rgba(128, 128, 128, 0.3)')
        
        fig.add_trace(go.Scatter(
            x=[start_date, end_date],
            y=[price, price],
            mode='lines',
            name=f'Fib {level_name}',
            line=dict(color=color, width=2, dash='dash'),
            showlegend=True,
            hovertemplate=f'Fib {level_name}: %{{y:.2f}}<extra></extra>'
        ))
    
    golden_zone_high = levels['0.786']
    golden_zone_low = levels['0.826']
    
    fig.add_trace(go.Scatter(
        x=[start_date, end_date, end_date, start_date, start_date],
        y=[golden_zone_high, golden_zone_high, golden_zone_low, golden_zone_low, golden_zone_high],
        fill='toself',
        fillcolor='rgba(255, 215, 0, 0.1)',
        line=dict(color='rgba(255, 215, 0, 0)', width=0),
        name='Golden Zone',
        showlegend=True,
        hoverinfo='skip'
    ))
    
    return fig


def add_bx_trender_subplot(
    fig: go.Figure,
    df: pd.DataFrame,
    bx_values: pd.Series,
    row: int = 2
) -> go.Figure:
    colors = []
    for i in range(len(bx_values)):
        val = bx_values.iloc[i]
        prev_val = bx_values.iloc[i-1] if i > 0 else val
        
        if val > 0 and val > prev_val:
            colors.append('#00ff00')
        elif val > 0 and val <= prev_val:
            colors.append('#228B22')
        elif val < 0 and val > prev_val:
            colors.append('#ff0000')
        else:
            colors.append('#8B0000')
    
    fig.add_trace(go.Bar(
        x=df.index,
        y=bx_values,
        name='BX-Trender',
        marker_color=colors,
        showlegend=True,
        hovertemplate='BX-Trender: %{y:.2f}<extra></extra>'
    ), row=row, col=1)
    
    fig.add_hline(y=0, line_dash="dash", line_color="gray", row=row, col=1)
    
    return fig
