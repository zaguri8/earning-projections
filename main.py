import argparse
import subprocess
import sys

parser = argparse.ArgumentParser(description="Run the following commands:")
parser.add_argument("--filings", action="store_true", help="Run filings", default=True)
parser.add_argument("--projections", action="store_true", help="Run projections", default=True)
parser.add_argument("--charting", action="store_true", help="Run charting", default=True)
parser.add_argument("--ticker", type=str, default="AAPL", help="Ticker to run")
parser.add_argument("--growth-bear", type=float, default=0.02, help="Growth rate for bear case (default: 0.02)")
parser.add_argument("--growth-base", type=float, default=0.05, help="Growth rate for base case (default: 0.05)")
parser.add_argument("--growth-bull", type=float, default=0.09, help="Growth rate for bull case (default: 0.09)")
parser.add_argument("--pe-bear", type=float, default=25, help="P/E ratio for Bear case (default: 25)")
parser.add_argument("--pe-base", type=float, default=30, help="P/E ratio for Base case (default: 30)")
parser.add_argument("--pe-bull", type=float, default=35, help="P/E ratio for Bull case (default: 35)")
parser.add_argument("--current-price", type=float, default=201, help="Current stock price (default: 201)")
args = parser.parse_args()

if __name__ == "__main__":
    #use shell to run the following commands sequentially with the current venv:
    # python filings/main.py --ticker AAPL --start-year 2020 --end-year 2024
    # python projections/main.py --ticker AAPL
    # python charting/main.py --ticker AAPL
    
    if args.filings:
        print(f"Running filings analysis for {args.ticker}...")
        try:
            result = subprocess.run([
                sys.executable, "filings/main.py", 
                "--ticker", args.ticker, 
                "--start-year", "2020", 
                "--end-year", "2024",
            ], check=True)
            print("Filings analysis completed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Filings analysis failed: {e}")
            sys.exit(1)  # Exit if filings fail
    
    if args.projections:
        print(f"Running projections analysis for {args.ticker}...")
        try:
            result = subprocess.run([
                sys.executable, "projections/main.py", 
                "--ticker", args.ticker,
                "--growth-bear", str(args.growth_bear),
                "--growth-base", str(args.growth_base),
                "--growth-bull", str(args.growth_bull),
            ], check=True)
            print("Projections analysis completed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Projections analysis failed: {e}")
            sys.exit(1)  # Exit if projections fail
    
    if args.charting:
        print(f"Running charting analysis for {args.ticker}...")
        try:
            result = subprocess.run([
                sys.executable, "charting/main.py", 
                "--ticker", args.ticker,
                "--pe-bear", str(args.pe_bear),
                "--pe-base", str(args.pe_base),
                "--pe-bull", str(args.pe_bull),
                "--current-price", str(args.current_price),
            ], check=True)
            print("Charting analysis completed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Charting analysis failed: {e}")
            sys.exit(1)  # Exit if charting fail
    
    print("All analyses completed successfully!")
