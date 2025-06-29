#!/usr/bin/env python3
"""
Centralized Financial Analysis Command System
Following Bjarne Stroustrup's design principles:
- Clean separation of concerns
- Modular command structure
- Clear interface boundaries
- Consistent parameter passing
"""

import argparse
import subprocess
import sys
from pathlib import Path

def create_parser():
    """Create the main argument parser with subcommands for each module"""
    parser = argparse.ArgumentParser(
        description="Financial Analysis Pipeline - Centralized Command System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s run-all --ticker AAPL                    # Run complete pipeline
  %(prog)s filings --ticker GTLB --start-year 2020  # Run filings only
  %(prog)s projections --ticker GTLB --profit-margin-target 0.15
  %(prog)s charting --ticker GTLB --target-pe 25
        """
    )
    
    # Global arguments that apply to all commands
    parser.add_argument('--ticker', type=str, default='AAPL', 
                       help='Stock ticker symbol (default: AAPL)')
    
    # Create subparsers for each module
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # ===== FILINGS SUBCOMMAND =====
    filings_parser = subparsers.add_parser('filings', help='Download and parse SEC filings')
    filings_parser.add_argument('--start-year', type=int, default=2020,
                               help='Start year for filings (default: 2020)')
    filings_parser.add_argument('--end-year', type=int, default=2024,
                               help='End year for filings (default: 2024)')
    filings_parser.add_argument('--filings-output-dir', type=str, 
                               default=str(Path(__file__).parent / "filings/output"),
                               help='Output directory for filing data')
    
    # ===== PROJECTIONS SUBCOMMAND =====
    projections_parser = subparsers.add_parser('projections', help='Generate financial projections')
    projections_parser.add_argument('--years-back', type=int, default=5,
                                   help='Number of historical years to fetch (default: 5)')
    projections_parser.add_argument('--current-year', type=int, default=2025,
                                   help='Base year for projections (default: 2025)')
    projections_parser.add_argument('--proj-years', type=int, default=5,
                                   help='Number of years to project (default: 5)')
    projections_parser.add_argument('--growth-bear', type=float, default=0.02,
                                   help='Growth rate for bear case (default: 0.02)')
    projections_parser.add_argument('--growth-base', type=float, default=0.05,
                                   help='Growth rate for base case (default: 0.05)')
    projections_parser.add_argument('--growth-bull', type=float, default=0.09,
                                   help='Growth rate for bull case (default: 0.09)')
    projections_parser.add_argument('--profit-margin-target', type=float, default=0.15,
                                   help='Target profit margin for unprofitable companies (default: 0.15)')
    projections_parser.add_argument('--years-to-profitability', type=int, default=5,
                                   help='Years to reach target profitability (default: 5)')
    projections_parser.add_argument('--projections-input-dir', type=str,
                                   default=str(Path(__file__).parent / "filings/output"),
                                   help='Input directory for filing data')
    projections_parser.add_argument('--projections-output-dir', type=str,
                                   default=str(Path(__file__).parent / "projections/output"),
                                   help='Output directory for projections')
    
    # ===== CHARTING SUBCOMMAND =====
    charting_parser = subparsers.add_parser('charting', help='Generate charts and visualizations')
    charting_parser.add_argument('--pe-bear', type=float, default=25,
                                help='P/E ratio for Bear case (default: 25)')
    charting_parser.add_argument('--pe-base', type=float, default=30,
                                help='P/E ratio for Base case (default: 30)')
    charting_parser.add_argument('--pe-bull', type=float, default=35,
                                help='P/E ratio for Bull case (default: 35)')
    charting_parser.add_argument('--target-pe', type=float, default=30,
                                help='Target P/E ratio for unprofitable companies (default: 30)')
    charting_parser.add_argument('--charting-years-to-profitability', type=int, default=3,
                                help='Years to reach target profitability for price projections (default: 3)')
    charting_parser.add_argument('--current-year', type=str, default='2025',
                                help='Current year (default: 2025)')
    charting_parser.add_argument('--current-price', type=float, default=201,
                                help='Current stock price (default: 201)')
    charting_parser.add_argument('--charting-input-dir', type=str,
                                default=str(Path(__file__).parent / "projections/output"),
                                help='Input directory for projection data')
    charting_parser.add_argument('--charting-output-dir', type=str,
                                default=str(Path(__file__).parent / "charting/output"),
                                help='Output directory for charts')
    charting_parser.add_argument('--download', action='store_true', default=True,
                                help='Download revenue tables as PNG files')
    charting_parser.add_argument('--charts', action='store_true', default=False,
                                help='Show interactive charts')
    charting_parser.add_argument('--port', type=int, default=8050,
                                help='Port for Dash app (default: 8050)')
    
    # ===== RUN-ALL SUBCOMMAND =====
    run_all_parser = subparsers.add_parser('run-all', help='Run complete pipeline (filings -> projections -> charting)')
    # Add common arguments for run-all
    run_all_parser.add_argument('--start-year', type=int, default=2020,
                               help='Start year for filings (default: 2020)')
    run_all_parser.add_argument('--end-year', type=int, default=2024,
                               help='End year for filings (default: 2024)')
    run_all_parser.add_argument('--filings-output-dir', type=str,
                               default=str(Path(__file__).parent / "filings/output"),
                               help='Output directory for filing data')
    run_all_parser.add_argument('--years-back', type=int, default=5,
                               help='Number of historical years to fetch (default: 5)')
    run_all_parser.add_argument('--current-year', type=int, default=2025,
                               help='Base year for projections (default: 2025)')
    run_all_parser.add_argument('--proj-years', type=int, default=5,
                               help='Number of years to project (default: 5)')
    run_all_parser.add_argument('--growth-bear', type=float, default=0.02,
                               help='Growth rate for bear case (default: 0.02)')
    run_all_parser.add_argument('--growth-base', type=float, default=0.05,
                               help='Growth rate for base case (default: 0.05)')
    run_all_parser.add_argument('--growth-bull', type=float, default=0.09,
                               help='Growth rate for bull case (default: 0.09)')
    run_all_parser.add_argument('--profit-margin-target', type=float, default=0.15,
                               help='Target profit margin for unprofitable companies (default: 0.15)')
    run_all_parser.add_argument('--years-to-profitability', type=int, default=5,
                               help='Years to reach target profitability (default: 5)')
    run_all_parser.add_argument('--projections-input-dir', type=str,
                               default=str(Path(__file__).parent / "filings/output"),
                               help='Input directory for filing data')
    run_all_parser.add_argument('--projections-output-dir', type=str,
                               default=str(Path(__file__).parent / "projections/output"),
                               help='Output directory for projections')
    run_all_parser.add_argument('--pe-bear', type=float, default=25,
                               help='P/E ratio for Bear case (default: 25)')
    run_all_parser.add_argument('--pe-base', type=float, default=30,
                               help='P/E ratio for Base case (default: 30)')
    run_all_parser.add_argument('--pe-bull', type=float, default=35,
                               help='P/E ratio for Bull case (default: 35)')
    run_all_parser.add_argument('--target-pe', type=float, default=30,
                               help='Target P/E ratio for unprofitable companies (default: 30)')
    run_all_parser.add_argument('--charting-years-to-profitability', type=int, default=3,
                               help='Years to reach target profitability for price projections (default: 3)')
    run_all_parser.add_argument('--current-price', type=float, default=201,
                               help='Current stock price (default: 201)')
    run_all_parser.add_argument('--charting-input-dir', type=str,
                               default=str(Path(__file__).parent / "projections/output"),
                               help='Input directory for projection data')
    run_all_parser.add_argument('--charting-output-dir', type=str,
                               default=str(Path(__file__).parent / "charting/output"),
                               help='Output directory for charts')
    run_all_parser.add_argument('--download', action='store_true', default=True,
                               help='Download revenue tables as PNG files')
    run_all_parser.add_argument('--charts', action='store_true', default=False,
                               help='Show interactive charts')
    run_all_parser.add_argument('--port', type=int, default=8050,
                               help='Port for Dash app (default: 8050)')
    
    return parser

def run_filings(args):
    """Execute filings module"""
    print(f"📄 Running filings analysis for {args.ticker}...")
    cmd = [
        sys.executable, "filings/main.py",
        "--ticker", args.ticker,
        "--start-year", str(args.start_year),
        "--end-year", str(args.end_year),
        "--output-dir", args.filings_output_dir
    ]
    return subprocess.run(cmd, check=True)

def run_projections(args):
    """Execute projections module"""
    print(f"📊 Running projections analysis for {args.ticker}...")
    cmd = [
        sys.executable, "projections/main.py",
        "--ticker", args.ticker,
        "--years-back", str(args.years_back),
        "--current-year", str(args.current_year),
        "--proj-years", str(args.proj_years),
        "--growth-bear", str(args.growth_bear),
        "--growth-base", str(args.growth_base),
        "--growth-bull", str(args.growth_bull),
        "--profit-margin-target", str(args.profit_margin_target),
        "--years-to-profitability", str(args.years_to_profitability),
        "--input-dir", args.projections_input_dir,
        "--output-dir", args.projections_output_dir
    ]
    return subprocess.run(cmd, check=True)

def run_charting(args):
    """Execute charting module"""
    print(f"\U0001F4C8 Running charting analysis for {args.ticker}...")
    cmd = [
        sys.executable, "charting/main.py",
        "--ticker", args.ticker,
        "--pe-bear", str(args.pe_bear),
        "--pe-base", str(args.pe_base),
        "--pe-bull", str(args.pe_bull),
        "--target-pe", str(args.target_pe),
        "--years-to-profitability", str(args.charting_years_to_profitability),
        "--current-year", str(args.current_year),
        "--current-price", str(args.current_price),
        "--input-dir", str(args.charting_input_dir),
        "--output-dir", str(args.charting_output_dir)
    ]
    if args.download:
        cmd.append("--download")
    if args.charts:
        cmd.append("--charts")
    cmd.extend(["--port", str(args.port)])
    return subprocess.run(cmd, check=True)

def main():
    """Main entry point with centralized command routing"""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'filings':
            run_filings(args)
            print("✅ Filings analysis completed successfully.")
            
        elif args.command == 'projections':
            run_projections(args)
            print("✅ Projections analysis completed successfully.")
            
        elif args.command == 'charting':
            run_charting(args)
            print("✅ Charting analysis completed successfully.")
            
        elif args.command == 'run-all':
            print(f"🚀 Running complete pipeline for {args.ticker}...")
            run_filings(args)
            print("✅ Filings completed.")
            run_projections(args)
            print("✅ Projections completed.")
            run_charting(args)
            print("✅ Charting completed.")
            print("🎉 Complete pipeline finished successfully!")
            
    except subprocess.CalledProcessError as e:
        print(f"❌ {args.command} failed with exit code {e.returncode}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
