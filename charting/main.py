import argparse
from pathlib import Path
from config import DashboardConfig, ScenarioConfig, ConfigManager
from data_manager import DataManager
from formatters import DataFormatter
from chart_generator import ChartGenerator
from dashboard_generator import DashboardGenerator
from exporter import DataExporter

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Scalable Financial Model Dashboard')
    parser.add_argument('--ticker', type=str, default='AAPL', help='Stock ticker symbol')
    parser.add_argument('--input-dir', type=str, default='./output', help='Input directory')
    parser.add_argument('--output-dir', type=str, default='./exports', help='Output directory')
    parser.add_argument('--current-year', type=str, default='2025', help='Current year')
    parser.add_argument('--current-price', type=float, default=201, help='Current stock price')
    parser.add_argument('--pe-bear', type=float, default=25, help='Bear case PE ratio')
    parser.add_argument('--pe-base', type=float, default=30, help='Base case PE ratio')
    parser.add_argument('--pe-bull', type=float, default=35, help='Bull case PE ratio')
    parser.add_argument('--target-pe', type=float, default=30, help='Target PE for unprofitable companies')
    parser.add_argument('--years-to-profitability', type=int, default=3, help='Years to profitability')
    parser.add_argument('--port', type=int, default=8050, help='Dashboard port')
    parser.add_argument('--export', action='store_true', help='Export tables as PNG')
    parser.add_argument('--run-dashboard', action='store_true', help='Run interactive dashboard')
    
    return parser.parse_args()

def create_config(args) -> DashboardConfig:
    """Create configuration from arguments"""
    scenarios = [
        ScenarioConfig("bear", "Bear Case", "#ce3c3c", args.pe_bear),
        ScenarioConfig("base", "Base Case", "#368fc7", args.pe_base),
        ScenarioConfig("bull", "Bull Case", "#18a551", args.pe_bull),
        ScenarioConfig("historical", "Historical", "#444", args.pe_base),
    ]
    
    return DashboardConfig(
        ticker=args.ticker,
        current_year=args.current_year,
        current_price=args.current_price,
        data_dir=Path(args.input_dir),
        output_dir=Path(args.output_dir),
        scenarios=scenarios,
        metrics=ConfigManager.get_default_metrics(),
        target_pe=args.target_pe,
        years_to_profitability=args.years_to_profitability,
        port=args.port
    )

def main():
    """Main application entry point"""
    args = parse_arguments()
    config = create_config(args)
    
    # Initialize components
    data_manager = DataManager(config)
    formatter = DataFormatter()
    chart_generator = ChartGenerator(config, formatter)
    
    # Load and validate data
    data = data_manager.load_all_data()
    if not data_manager.validate_data(data):
        return
    
    # Export if requested
    if args.export:
        exporter = DataExporter(config, chart_generator)
        exporter.export_scenario_tables(data)
        print("Export completed")
    
    # Run dashboard if requested
    if args.run_dashboard:
        dashboard_generator = DashboardGenerator(config, data_manager, chart_generator, formatter)
        app = dashboard_generator.create_dashboard(data)
        app.run_server(debug=True, port=config.port)

if __name__ == "__main__":
    main()