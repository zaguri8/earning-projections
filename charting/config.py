from dataclasses import dataclass
from typing import Dict, List, Optional
from pathlib import Path

@dataclass
class MetricConfig:
    """Configuration for a financial metric"""
    name: str
    display_name: str
    format_type: str  # 'currency', 'percentage', 'number', 'price'
    unit: str = ""
    show_growth: bool = True
    chart_color: str = "#1f77b4"

@dataclass
class ScenarioConfig:
    """Configuration for a financial scenario"""
    name: str
    display_name: str
    color: str
    pe_ratio: float

@dataclass
class DashboardConfig:
    """Main dashboard configuration"""
    ticker: str
    current_year: str
    current_price: float
    data_dir: Path
    output_dir: Path
    scenarios: List[ScenarioConfig]
    metrics: List[MetricConfig]
    target_pe: float = 30.0
    years_to_profitability: int = 3
    port: int = 8050

class ConfigManager:
    """Manages configuration and provides default settings"""
    
    @staticmethod
    def get_default_metrics() -> List[MetricConfig]:
        return [
            MetricConfig("revenue", "Revenue", "currency", show_growth=True),
            MetricConfig("net_income", "Net Income", "currency", show_growth=True),
            MetricConfig("eps", "EPS", "price", show_growth=True),
            MetricConfig("fcf", "Free Cash Flow", "currency", show_growth=True),
            MetricConfig("gross_margin", "Gross Margin", "percentage", show_growth=False),
            MetricConfig("operating_margin", "Operating Margin", "percentage", show_growth=False),
            MetricConfig("net_margin", "Net Margin", "percentage", show_growth=False),
            MetricConfig("fcf_margin", "FCF Margin", "percentage", show_growth=False),
        ]
    
    @staticmethod
    def get_default_scenarios() -> List[ScenarioConfig]:
        return [
            ScenarioConfig("bear", "Bear Case", "#ce3c3c", 25.0),
            ScenarioConfig("base", "Base Case", "#368fc7", 30.0),
            ScenarioConfig("bull", "Bull Case", "#18a551", 35.0),
            ScenarioConfig("historical", "Historical", "#444", 25.0),
        ]