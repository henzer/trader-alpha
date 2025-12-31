import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from pathlib import Path
from typing import Optional
from .charts import (
    create_candlestick_chart,
    add_market_bias,
    add_fibonacci_levels,
    add_bx_trender_subplot
)


class StockChart:
    def __init__(self, symbol: str, df: pd.DataFrame):
        self.symbol = symbol
        self.df = df
        self.fig = None
        self.score_data = None
        
    def set_score_data(self, score_breakdown: dict) -> 'StockChart':
        self.score_data = score_breakdown
        return self
        
    def create_base_chart(self, with_bx_trender: bool = True, bx_rows: int = 1) -> 'StockChart':
        if with_bx_trender:
            if bx_rows == 2:
                row_heights = [0.6, 0.2, 0.2]
                self.fig = make_subplots(
                    rows=3, cols=1,
                    shared_xaxes=True,
                    vertical_spacing=0.03,
                    row_heights=row_heights,
                    specs=[[{"secondary_y": False}],
                           [{"secondary_y": False}],
                           [{"secondary_y": False}]]
                )
            elif bx_rows == 3:
                row_heights = [0.5, 0.15, 0.15, 0.2]
                subplot_titles = (
                    f'{self.symbol} - Price Action',
                    'Monthly BX-Trender',
                    'Weekly BX-Trender',
                    'Daily BX-Trender'
                )
                self.fig = make_subplots(
                    rows=4, cols=1,
                    shared_xaxes=True,
                    vertical_spacing=0.02,
                    row_heights=row_heights,
                    subplot_titles=subplot_titles
                )
            else:
                self.fig = make_subplots(
                    rows=2, cols=1,
                    shared_xaxes=True,
                    vertical_spacing=0.03,
                    row_heights=[0.7, 0.3],
                    subplot_titles=(f'{self.symbol} - Price Action', 'BX-Trender Oscillator')
                )
            
            self.fig.add_trace(go.Candlestick(
                x=self.df.index,
                open=self.df['open'],
                high=self.df['high'],
                low=self.df['low'],
                close=self.df['close'],
                name='OHLC',
                increasing_line_color='#26a69a',
                decreasing_line_color='#ef5350'
            ), row=1, col=1)
            
            self.fig.update_layout(
                template='plotly_dark',
                height=800,
                title=dict(
                    text=f'{self.symbol} - Price Action & Indicators',
                    x=0.5,
                    xanchor='center'
                ),
                xaxis_rangeslider_visible=False,
                hovermode='x unified',
                showlegend=True,
                legend=dict(
                    yanchor="top",
                    y=0.99,
                    xanchor="left",
                    x=0.01
                )
            )
            
            self.fig.update_yaxes(title_text="Price (USD)", row=1, col=1)
            self.fig.update_yaxes(title_text="Monthly BX-Trender", row=2, col=1)
            self.fig.update_yaxes(title_text="Weekly BX-Trender", row=3, col=1)
            self.fig.update_xaxes(title_text="Date", row=3, col=1)
            
            rangebreaks_config = [
                dict(bounds=["sat", "mon"]),
                dict(values=["2024-12-25", "2025-01-01"])
            ]
            
            self.fig.update_xaxes(rangebreaks=rangebreaks_config, row=1, col=1)
            self.fig.update_xaxes(rangebreaks=rangebreaks_config, row=2, col=1)
            self.fig.update_xaxes(rangebreaks=rangebreaks_config, row=3, col=1)
        else:
            self.fig = create_candlestick_chart(self.df, self.symbol)
        
        return self
    
    def add_market_bias(
        self, 
        bias_high: pd.Series, 
        bias_low: pd.Series, 
        name: str = "Market Bias",
        df_index: Optional[pd.DatetimeIndex] = None,
        resample_to_daily: bool = False,
        color: str = 'green'
    ) -> 'StockChart':
        if self.fig is None:
            raise ValueError("Create base chart first")
        
        index_to_use = df_index if df_index is not None else bias_high.index
        high_to_use = bias_high
        low_to_use = bias_low
        
        if resample_to_daily:
            df_temp_high = pd.DataFrame({'value': bias_high}, index=index_to_use)
            df_temp_high = df_temp_high.reindex(self.df.index, method='ffill')
            
            df_temp_low = pd.DataFrame({'value': bias_low}, index=index_to_use)
            df_temp_low = df_temp_low.reindex(self.df.index, method='ffill')
            
            index_to_use = df_temp_high.index
            high_to_use = df_temp_high['value']
            low_to_use = df_temp_low['value']
        
        color_map = {
            'green': 'rgba(0, 255, 0, 0.15)',
            'blue': 'rgba(0, 150, 255, 0.15)',
            'yellow': 'rgba(255, 255, 0, 0.15)'
        }
        
        fillcolor = color_map.get(color, 'rgba(0, 255, 0, 0.15)')
        
        self.fig.add_trace(go.Scatter(
            x=index_to_use,
            y=high_to_use,
            mode='lines',
            name=f'{name} High',
            line=dict(color='rgba(0, 0, 0, 0)', width=0),
            showlegend=False,
            hoverinfo='skip'
        ), row=1, col=1)
        
        self.fig.add_trace(go.Scatter(
            x=index_to_use,
            y=low_to_use,
            mode='lines',
            name=name,
            line=dict(color='rgba(0, 0, 0, 0)', width=0),
            fill='tonexty',
            fillcolor=fillcolor,
            showlegend=True,
            hovertemplate=f'{name}<br>High: %{{y:.2f}}<extra></extra>'
        ), row=1, col=1)
        
        return self
    
    def add_fibonacci(
        self,
        swing_high: float,
        swing_low: float,
        show_all_levels: bool = False
    ) -> 'StockChart':
        if self.fig is None:
            raise ValueError("Create base chart first")
        
        start_date = self.df.index[0]
        end_date = self.df.index[-1]
        
        diff = swing_high - swing_low
        
        levels = {
            '0.618': swing_high - (diff * 0.618),
            '0.786': swing_high - (diff * 0.786),
            '0.826': swing_high - (diff * 0.826),
        }
        
        if show_all_levels:
            levels.update({
                '0.0': swing_high,
                '0.236': swing_high - (diff * 0.236),
                '0.382': swing_high - (diff * 0.382),
                '0.5': swing_high - (diff * 0.5),
                '1.0': swing_low
            })
        
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
        
        self.fig.add_trace(go.Scatter(
            x=[start_date, end_date],
            y=[swing_high, swing_high],
            mode='lines',
            name='Take Profit (Swing High)',
            line=dict(color='rgba(0, 255, 0, 0.8)', width=3, dash='solid'),
            showlegend=True,
            hovertemplate=f'TP: %{{y:.2f}}<extra></extra>'
        ), row=1, col=1)
        
        self.fig.add_trace(go.Scatter(
            x=[start_date, end_date],
            y=[swing_low, swing_low],
            mode='lines',
            name='Stop Loss (Swing Low)',
            line=dict(color='rgba(255, 0, 0, 0.8)', width=3, dash='solid'),
            showlegend=True,
            hovertemplate=f'SL: %{{y:.2f}}<extra></extra>'
        ), row=1, col=1)
        
        for level_name, price in levels.items():
            color = colors.get(level_name, 'rgba(128, 128, 128, 0.3)')
            
            self.fig.add_trace(go.Scatter(
                x=[start_date, end_date],
                y=[price, price],
                mode='lines',
                name=f'Fib {level_name}',
                line=dict(color=color, width=2, dash='dash'),
                showlegend=True,
                hovertemplate=f'Fib {level_name}: %{{y:.2f}}<extra></extra>'
            ), row=1, col=1)
        
        golden_zone_high = levels['0.786']
        golden_zone_low = levels['0.826']
        
        self.fig.add_trace(go.Scatter(
            x=[start_date, end_date, end_date, start_date, start_date],
            y=[golden_zone_high, golden_zone_high, golden_zone_low, golden_zone_low, golden_zone_high],
            fill='toself',
            fillcolor='rgba(255, 215, 0, 0.1)',
            line=dict(color='rgba(255, 215, 0, 0)', width=0),
            name='Golden Zone',
            showlegend=True,
            hoverinfo='skip'
        ), row=1, col=1)
        
        return self
    
    def add_bx_trender(
        self, 
        bx_values: pd.Series, 
        row: int = 2, 
        name: str = 'BX-Trender',
        df_index: Optional[pd.DatetimeIndex] = None,
        resample_to_daily: bool = False
    ) -> 'StockChart':
        if self.fig is None:
            raise ValueError("Create base chart first")
        
        index_to_use = df_index if df_index is not None else self.df.index
        
        colors_map = {}
        for i in range(len(bx_values)):
            val = bx_values.iloc[i]
            prev_val = bx_values.iloc[i-1] if i > 0 else val
            date = bx_values.index[i]
            
            if val > 0 and val > prev_val:
                color = '#00ff00'
            elif val > 0 and val <= prev_val:
                color = '#228B22'
            elif val < 0 and val > prev_val:
                color = '#ff0000'
            else:
                color = '#8B0000'
            
            colors_map[date] = color
        
        if resample_to_daily:
            daily_values = []
            daily_colors = []
            
            for daily_date in self.df.index:
                matching_date = None
                for orig_date in index_to_use:
                    if daily_date >= orig_date:
                        matching_date = orig_date
                    else:
                        break
                
                if matching_date is not None:
                    idx = bx_values.index.get_loc(matching_date)
                    daily_values.append(bx_values.iloc[idx])
                    daily_colors.append(colors_map[matching_date])
                else:
                    daily_values.append(None)
                    daily_colors.append('#808080')
            
            index_to_use = self.df.index
            values_to_use = daily_values
            colors = daily_colors
        else:
            values_to_use = bx_values
            colors = [colors_map[date] for date in bx_values.index]
        
        self.fig.add_trace(go.Bar(
            x=index_to_use,
            y=values_to_use,
            name=name,
            marker_color=colors,
            showlegend=True,
            hovertemplate=f'{name}: %{{y:.2f}}<extra></extra>'
        ), row=row, col=1)
        
        self.fig.add_hline(y=0, line_dash="dash", line_color="gray", row=row, col=1)
        
        return self
    
    def add_score_annotation(self) -> 'StockChart':
        if self.fig is None:
            raise ValueError("Create base chart first")
        
        if self.score_data is None:
            return self
        
        total_score = self.score_data.get('total_score', 0)
        passed_filter = self.score_data.get('passed_filter', False)
        mb_score = self.score_data.get('market_bias_score', 0)
        mb_tf = self.score_data.get('market_bias_timeframe', 'N/A')
        fib_score = self.score_data.get('fibonacci_score', 0)
        fib_zone = self.score_data.get('fibonacci_zone', 'N/A')
        bx_color = self.score_data.get('bx_trender_color', 'N/A')
        
        filter_emoji = "✅" if passed_filter else "❌"
        filter_text = "PASS" if passed_filter else "FAIL"
        
        score_text = f"""<b>SCORE: {total_score}/11</b><br>
Filter: {filter_emoji} {filter_text}<br>
BX-Trender: {bx_color}<br>
<br>
<b>Breakdown:</b><br>
Market Bias: {mb_score} pts ({mb_tf})<br>
Fibonacci: {fib_score} pts ({fib_zone})"""
        
        self.fig.add_annotation(
            xref="paper", yref="paper",
            x=0.02, y=0.02,
            xanchor='left', yanchor='bottom',
            text=score_text,
            showarrow=False,
            font=dict(size=12, color="white"),
            bgcolor="rgba(0, 0, 0, 0.8)",
            bordercolor="white",
            borderwidth=2,
            borderpad=10,
            align='left'
        )
        
        return self
    
    def save(self, output_path: Optional[str] = None) -> str:
        if self.fig is None:
            raise ValueError("No chart to save. Create chart first.")
        
        if output_path is None:
            output_dir = Path(__file__).parent.parent / "output"
            output_dir.mkdir(exist_ok=True)
            output_path = str(output_dir / f"{self.symbol}_chart.html")
        
        self.fig.write_html(output_path)
        return output_path
    
    def show(self):
        if self.fig is None:
            raise ValueError("No chart to show. Create chart first.")
        self.fig.show()
