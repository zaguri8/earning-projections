"""SEC 10-K Financial Model with Improved Computations and Scalability"""

import os, json, datetime, argparse
from pathlib import Path
from typing import Dict, Tuple, Optional, List
from dataclasses import asdict

import pandas as pd
import numpy as np

from financial_model import FinancialModel, ProjectionParams

API_KEY = os.getenv("SEC_API_KEY") or "YOUR_API_KEY"
CURRENT_DIR = Path(__file__).parent
DEBUG = True

def debug_print(msg):
    if DEBUG:
        print(f"[DEBUG] {msg}")

# -------------------------------------------------------------------- #
#  File Loading Functions (kept for compatibility)
# -------------------------------------------------------------------- #
def _list_available_files(input_dir: str = "./input") -> dict:
    """List available files and extract ticker/year info"""
    input_path = Path(input_dir)
    if not input_path.exists():
        return {}
    
    available = {}
    for json_file in input_path.glob("*.json"):
        filename = json_file.stem
        # Try to extract ticker and year from filename
        parts = filename.split('_')
        if len(parts) >= 2:
            ticker = parts[0].upper()
            try:
                year = int(parts[1])
                if ticker not in available:
                    available[ticker] = []
                available[ticker].append(year)
            except ValueError:
                continue
    
    return available

# -------------------------------------------------------------------- #
#  Main Projection Function (updated to use financial model)
# -------------------------------------------------------------------- #
def build_projections(ticker: str, years_back: int = 5, current_year: int = 2025, proj_years: int = 5,
                     growth: Optional[Dict[str, Dict[str, float]]] = {"revenue": {"bear": 0.02, "base": 0.05, "bull": 0.09}},
                     out_dir: Optional[str] = None, from_files: bool = False, input_dir: str = "./input",
                     profit_margin_target: Optional[float] = 0.15, years_to_profitability: int = 5,
                     margin_growth: Optional[Dict[str, float]] = None) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Build projections starting from current_year for proj_years using financial model
    
    Args:
        ticker: Stock ticker symbol
        years_back: Number of historical years to fetch (from current_year-1 backwards)
        current_year: Base year for projections (default 2025)
        proj_years: Number of years to project forward (default 5 for current_year-current_year+4)
        growth: Growth rate assumptions
        out_dir: Output directory
        from_files: Whether to load from local files instead of SEC API
        input_dir: Directory containing input files when from_files=True
        profit_margin_target: Target profit margin to reach (e.g., 0.15 for 15% margin)
        years_to_profitability: Years to reach target profitability
        margin_growth: Annual margin growth for profitable companies
    """
    
    if from_files:
        print(f"Loading data from files in: {input_dir}")
        available = _list_available_files(input_dir)
        if ticker.upper() in available:
            print(f"Available years for {ticker}: {sorted(available[ticker.upper()])}")
    
    # Create financial model instance
    model = FinancialModel(API_KEY)
    
    # Create projection parameters
    params = ProjectionParams(
        revenue_growth=growth.get("revenue", {"bear": 0.02, "base": 0.05, "bull": 0.09}),
        years_back=years_back,
        current_year=current_year,
        proj_years=proj_years,
        profit_margin_target=profit_margin_target,
        years_to_profitability=years_to_profitability,
        margin_growth=margin_growth,
        terminal_growth_rate=0.025,
        discount_rate=0.10
    )
    
    # Run comprehensive analysis
    results = model.run_comprehensive_analysis(
        ticker=ticker,
        params=params,
        from_files=from_files,
        input_dir=input_dir,
        output_dir=out_dir or f"./{ticker}_model"
    )
    
    # Save results in the expected format for backward compatibility
    directory = Path(out_dir or f"./{ticker}_model")
    directory.mkdir(exist_ok=True, parents=True)
    print("Writing CSVs to:", directory.resolve())
    
    # Save historical and projection data
    results['projections']['historical'].to_csv(directory / f"{ticker}_historical.csv")
    results['projections']['bear'].to_csv(directory / f"{ticker}_bear.csv")
    results['projections']['base'].to_csv(directory / f"{ticker}_base.csv")
    results['projections']['bull'].to_csv(directory / f"{ticker}_bull.csv")
    
    # Save results
    with open(directory / f"{ticker}_valuations.json", 'w') as f:
        json.dump(results['valuations'], f, indent=2)
    
    with open(directory / f"{ticker}_summary.json", 'w') as f:
        json.dump(results['summary_stats'], f, indent=2)
    
    return (results['projections']['historical'], 
            results['projections']['bear'], 
            results['projections']['base'], 
            results['projections']['bull'])

# -------------------------------------------------------------------- #
#  Test Functions (updated to use financial model)
# -------------------------------------------------------------------- #
def test_single_year(ticker: str, year: int, from_files: bool = False, input_dir: str = "./input"):
    """Test extraction for a single year using financial model"""
    debug_print(f"Testing {ticker} for year {year}")
    
    try:
        model = FinancialModel(API_KEY)
        
        if from_files:
            xbrl_data = model._load_from_file(ticker, year, input_dir)
        else:
            xbrl_data = model._fetch_from_api(ticker, year)
        
        debug_print(f"Available sections: {list(xbrl_data.keys())}")
        
        # Extract metrics using financial model
        metrics = model.extract_metrics_from_xbrl(xbrl_data, year)
        
        print(f"\nResults for {ticker} {year}:")
        for field_name, value in asdict(metrics).items():
            if value is not None:
                if isinstance(value, float) and abs(value) > 1000000:
                    print(f"  {field_name}: ${value:,.0f}")
                else:
                    print(f"  {field_name}: {value}")
            else:
                print(f"  {field_name}: None")
                
        return asdict(metrics)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def list_available_data(input_dir: str = "./input"):
    """List all available ticker data in the input directory"""
    available = _list_available_files(input_dir)
    if not available:
        print(f"No JSON files found in {input_dir}")
        return
    
    print(f"Available data in {input_dir}:")
    for ticker, years in available.items():
        print(f"  {ticker}: {sorted(years)}")

# -------------------------------------------------------------------- #
#  Main Execution
# -------------------------------------------------------------------- #
if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--ticker", type=str, default="AAPL", help="Ticker to run")
    p.add_argument("--year", type=int, help="Test specific year")
    p.add_argument("--years-back", type=int, default=4)
    now = datetime.datetime.now()
    p.add_argument("--current-year", type=int, default=now.year, help="Base year for projections (default: current year)")
    p.add_argument("--proj-years", type=int, default=5, help="Number of years to project (default: 5 for current_year-proj_years)")
    p.add_argument("--growth-bear", type=float, default=0.02, help="Growth rate for bear case (default: 0.02)")
    p.add_argument("--growth-base", type=float, default=0.05, help="Growth rate for base case (default: 0.05)")
    p.add_argument("--growth-bull", type=float, default=0.09, help="Growth rate for bull case (default: 0.09)")
    p.add_argument("--profit-margin-target", type=float, default=0.15, help="Target profit margin to reach (default: 0.15 for 15%)")
    p.add_argument("--years-to-profitability", type=int, default=5, help="Years to reach target profitability (default: 5)")
    p.add_argument("--margin-growth-bear", type=float, default=None, help="Annual margin growth for profitable companies in bear case (e.g., 0.02 for 2% growth)")
    p.add_argument("--margin-growth-base", type=float, default=None, help="Annual margin growth for profitable companies in base case (e.g., 0.02 for 2% growth)")
    p.add_argument("--margin-growth-bull", type=float, default=None, help="Annual margin growth for profitable companies in bull case (e.g., 0.02 for 2% growth)")
    p.add_argument("--output-dir", default=str(CURRENT_DIR / "output"))
    p.add_argument("--from-files", action="store_true", help="Load data from local files instead of SEC API", default=True)
    p.add_argument("--input-dir", default=str(CURRENT_DIR / "../filings/output"), help="Directory containing input JSON files")
    p.add_argument("--list-available", action="store_true", help="List available data files")
    args = p.parse_args()
    
    if args.list_available:
        list_available_data(args.input_dir)
    elif args.year:
        test_single_year(args.ticker, args.year, args.from_files, args.input_dir)
    else:
        # Run full projection
        try:
            # Prepare margin growth dict if any parameters are provided
            margin_growth = None
            if args.margin_growth_bear is not None or args.margin_growth_base is not None or args.margin_growth_bull is not None:
                margin_growth = {
                    "bear": args.margin_growth_bear,
                    "base": args.margin_growth_base,
                    "bull": args.margin_growth_bull
                }
            
            hist, bear, base, bull = build_projections(
                args.ticker, args.years_back, args.current_year, args.proj_years,
                {"revenue": {"bear": args.growth_bear, "base": args.growth_base, "bull": args.growth_bull}},
                args.output_dir, args.from_files, args.input_dir,
                args.profit_margin_target, args.years_to_profitability, margin_growth
            )
            print(f"\nProjections for {args.ticker} ({args.current_year}-{args.current_year + args.proj_years - 1}):")
            print(f"Target profit margin: {args.profit_margin_target:.1%}")
            print(f"Years to profitability: {args.years_to_profitability}")
            print("\nBase‑case preview:")
            print(base.iloc[:5, :])         # All columns, first 5 metrics
            print("\nDEBUG: shares_diluted in base-case projection:")
            print(base.loc[:, 'shares_diluted'])
            print("\nDEBUG: revenue in base-case projection:")
            print(base.loc[:, 'revenue'])
            print("\nDEBUG: net_income in base-case projection:")
            print(base.loc[:, 'net_income'])
            print("\nDEBUG: fcf in base-case projection:")
            print(base.loc[:, 'fcf'])
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()