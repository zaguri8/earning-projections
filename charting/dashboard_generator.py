import dash
from dash import html, dcc, dash_table
from typing import Dict
import pandas as pd
from config import DashboardConfig, ScenarioConfig
from data_manager import DataManager
from chart_generator import ChartGenerator
from formatters import DataFormatter
from price_projector import PriceProjector
from config import MetricConfig

class DashboardGenerator:
    """Generates the Dash dashboard"""
    
    def __init__(self, config: DashboardConfig, data_manager: DataManager, 
                 chart_generator: ChartGenerator, formatter: DataFormatter):
        self.config = config
        self.data_manager = data_manager
        self.chart_generator = chart_generator
        self.formatter = formatter
    
    def create_scenario_section(self, scenario: ScenarioConfig, 
                              df: pd.DataFrame) -> html.Div:
        """Create a complete section for a scenario"""
        df_transposed = df.transpose()
        
        # Add price projections
        scenario_config = next(s for s in self.config.scenarios if s.name == scenario.name)
        price_projector = PriceProjector(
            pe_ratio=scenario_config.pe_ratio,
            current_year=self.config.current_year,
            current_price=self.config.current_price,
            target_pe=self.config.target_pe,
            years_to_profitability=self.config.years_to_profitability
        )
        
        projected_prices = price_projector.project_prices(df_transposed)
        df_transposed.loc["Price"] = projected_prices
        
        # Create charts
        charts = []
        for metric in self.config.metrics + [MetricConfig("Price", "Price", "price", show_growth=False)]:
            if any(metric.name.lower() == idx.lower() for idx in df_transposed.index):
                chart = self.chart_generator.create_metric_chart(df_transposed, metric, scenario)
                if chart:
                    charts.append(dcc.Graph(figure=chart, style={"marginBottom": "32px"}))
        
        # Create table
        table_data = []
        for metric in self.config.metrics + [MetricConfig("Price", "Price", "price", show_growth=False)]:
            # Find actual metric name (case insensitive)
            actual_metric_name = None
            for idx in df_transposed.index:
                if idx.lower() == metric.name.lower():
                    actual_metric_name = idx
                    break
            
            if actual_metric_name is not None:
                row = {"Metric": metric.display_name}
                for col in df_transposed.columns:
                    val = df_transposed.loc[actual_metric_name, col]
                    formatted_val = self.formatter.format_value(val, metric.format_type)
                    row[str(col)] = formatted_val
                table_data.append(row)
        
        table_columns = [{"name": "Metric", "id": "Metric"}] + [
            {"name": str(col), "id": str(col)} for col in df_transposed.columns
        ]
        
        table = dash_table.DataTable(
            data=table_data,
            columns=table_columns,
            style_table={'overflowX': 'auto', "padding": "0", "marginBottom": "32px"},
            style_data={
                'backgroundColor': '#fff',
                'color': '#222',
                'fontSize': 16,
                'padding': "8px",
            },
            style_header={
                'backgroundColor': '#e9ecef',
                'fontWeight': 'bold',
                'fontSize': 17,
                'borderTop': '2px solid #ced4da',
                'borderBottom': '2px solid #ced4da'
            },
            style_cell={
                'textAlign': 'center',
                'minWidth': '90px', 'width': '90px', 'maxWidth': '120px',
                'padding': "8px"
            },
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': '#f6f8fa'
                },
                {
                    'if': {'column_id': 'Metric'},
                    'textAlign': 'left',
                    'fontWeight': 'bold',
                    'backgroundColor': '#f0f2f4'
                }
            ]
        )
        
        return html.Div([
            *charts,
            html.H4(f"{scenario.display_name} Table", 
                   style={"marginTop": "30px", "marginBottom": "10px"}),
            table
        ], style={
            "background": "#fff",
            "borderRadius": "18px",
            "boxShadow": "0 6px 24px 0 rgba(0,0,0,0.06)",
            "padding": "32px 32px 16px 32px",
            "marginBottom": "36px"
        })
    
    def create_dashboard(self, data: Dict[str, pd.DataFrame]) -> dash.Dash:
        """Create the complete dashboard"""
        app = dash.Dash(__name__)
        
        sections = []
        for scenario in self.config.scenarios:
            if scenario.name in data:
                section = self.create_scenario_section(scenario, data[scenario.name])
                sections.append(html.H2(scenario.display_name, 
                                      style={"marginTop":"12px", "color": scenario.color, 
                                           "fontFamily":"Inter, Arial, sans-serif"}))
                sections.append(section)
        
        app.layout = html.Div([
            html.H1(f"{self.config.ticker} Financial Model Dashboard", 
                   style={"marginTop":"28px", "marginBottom":"8px", 
                         "fontFamily":"Inter, Arial, sans-serif"}),
            html.H3("Financial Scenario Analysis", 
                   style={"color":"#444", "fontFamily":"Inter, Arial, sans-serif", 
                         "marginBottom":"22px"}),
            html.Div(sections, 
                    style={"overflowY": "auto", "height": "90vh", "padding": "30px"})
        ], style={
            "background": "#f3f4f7",
            "minHeight": "100vh",
            "fontFamily":"Inter, Arial, sans-serif"
        })
        
        return app
