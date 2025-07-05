import plotly.graph_objs as go
import plotly.io as pio
from typing import List, Tuple
import pandas as pd
from config import DashboardConfig, ScenarioConfig, MetricConfig
from formatters import DataFormatter
from price_projector import PriceProjector

class ChartGenerator:
    """Generates charts and visualizations"""
    
    def __init__(self, config: DashboardConfig, formatter: DataFormatter):
        self.config = config
        self.formatter = formatter
    
    def create_metric_chart(self, df: pd.DataFrame, metric: MetricConfig, 
                          scenario: ScenarioConfig) -> go.Figure:
        """Create a chart for a specific metric"""
        if metric.name not in df.index:
            return None
        
        values = df.loc[metric.name].values
        years = df.columns.tolist()
        
        # Calculate growth percentages
        growth_labels = [""]
        if metric.show_growth:
            for i in range(1, len(values)):
                growth = self.formatter.calculate_growth(values[i], values[i-1])
                growth_labels.append(growth)
        else:
            growth_labels.extend([""] * (len(values) - 1))
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=years,
            y=values,
            mode='lines+markers+text',
            name=scenario.display_name,
            text=growth_labels,
            textposition="top center",
            textfont=dict(size=13, color="black"),
            hovertemplate="%{y}<br>%{text} from last year<extra></extra>",
            marker=dict(size=8, color=scenario.color),
            line=dict(color=scenario.color)
        ))
        
        fig.update_layout(
            title=f"{metric.display_name} — {scenario.display_name}",
            legend=dict(x=0.01, y=0.98),
            margin={"r":0,"t":30,"l":0,"b":0},
            height=300,
            plot_bgcolor="#fafbfc",
            paper_bgcolor="#fafbfc",
            font=dict(family="Inter, Arial, sans-serif", size=15)
        )
        
        return fig
    
    def create_table_figure(self, df: pd.DataFrame, scenario: ScenarioConfig, 
                          price_projector: PriceProjector) -> go.Figure:
        """Create a table figure for export"""
        # Add price projections
        projected_prices = price_projector.project_prices(df)
        df_with_price = df.copy()
        df_with_price.loc["Price"] = projected_prices
        
        # Create table data
        table_data = []
        headers = ['Metric'] + [str(col) for col in df.columns]
        
        # Add metrics and their growth rates
        for metric_config in self.config.metrics + [MetricConfig("Price", "Price", "price", show_growth=False)]:
            if metric_config.name.lower() in [idx.lower() for idx in df_with_price.index]:
                # Find the actual index name (case insensitive)
                actual_metric_name = None
                for idx in df_with_price.index:
                    if idx.lower() == metric_config.name.lower():
                        actual_metric_name = idx
                        break
                
                if actual_metric_name is None:
                    continue
                
                # Add main metric row
                row = [metric_config.display_name]
                for col in df.columns:
                    val = df_with_price.loc[actual_metric_name, col]
                    formatted_val = self.formatter.format_value(val, metric_config.format_type)
                    row.append(formatted_val)
                table_data.append(row)
                
                # Add growth row for key metrics
                if metric_config.show_growth and metric_config.name in ["revenue", "net_income", "eps", "fcf"]:
                    growth_row = [f"{metric_config.display_name} Growth %"]
                    growth_row.append("")  # First year has no growth
                    
                    for i in range(1, len(df.columns)):
                        current_val = df_with_price.loc[actual_metric_name, df.columns[i]]
                        prev_val = df_with_price.loc[actual_metric_name, df.columns[i-1]]
                        growth = self.formatter.calculate_growth(current_val, prev_val)
                        growth_row.append(growth)
                    
                    table_data.append(growth_row)
        
        # Create figure
        fig = go.Figure(data=[go.Table(
            columnwidth=[180] + [80] * len(df.columns),
            header=dict(
                values=headers,
                fill_color='#e9ecef',
                font=dict(size=14, color='black', family='Arial, sans-serif'),
                align='center',
                height=35,
                line=dict(color='#ced4da', width=2)
            ),
            cells=dict(
                values=list(zip(*table_data)),
                fill_color=[['#f0f2f4', '#ffffff'] * (len(table_data)//2 + 1)][:len(table_data)],
                font=dict(size=12, color='black', family='Arial, sans-serif'),
                height=30,
                align='center',
                line=dict(color='#dee2e6', width=1)
            )
        )])
        
        # Set figure dimensions
        fig_height = max(600, 35 + (30 * len(table_data)) + 100)
        fig.update_layout(
            title=f"{self.config.ticker} - {scenario.display_name} Financial Projections",
            title_font=dict(size=16, family='Arial, sans-serif'),
            width=1000,
            height=fig_height,
            margin=dict(l=20, r=20, t=60, b=20),
            autosize=False
        )
        
        return fig
