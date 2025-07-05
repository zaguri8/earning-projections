import plotly.io as pio
from pathlib import Path
from config import DashboardConfig
from chart_generator import ChartGenerator
from price_projector import PriceProjector
from typing import Dict
import pandas as pd

class DataExporter:
    """Handles exporting data and charts"""
    
    def __init__(self, config: DashboardConfig, chart_generator: ChartGenerator):
        self.config = config
        self.chart_generator = chart_generator
    
    def export_scenario_tables(self, data: Dict[str, pd.DataFrame]):
        """Export tables for all scenarios as PNG files"""
        self.config.output_dir.mkdir(parents=True, exist_ok=True)
        
        for scenario in self.config.scenarios:
            if scenario.name in data and scenario.name != "historical":
                price_projector = PriceProjector(
                    pe_ratio=scenario.pe_ratio,
                    current_year=self.config.current_year,
                    current_price=self.config.current_price,
                    target_pe=self.config.target_pe,
                    years_to_profitability=self.config.years_to_profitability
                )
                
                df = data[scenario.name].transpose()
                fig = self.chart_generator.create_table_figure(df, scenario, price_projector)
                
                filename = self.config.output_dir / f"{self.config.ticker}_{scenario.name}_table.png"
                pio.write_image(fig, str(filename), format='png')
                print(f"Exported {filename}")
