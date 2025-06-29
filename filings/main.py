#!/usr/bin/env python3
"""
Download filings for a given ticker and save them to a directory.

Usage
-----
python filings.py --ticker AAPL --start-year 2020 --end-year 2024 --output-dir ./filings

python filings.py --ticker AAPL --start-year 2020 --end-year 2024 --output-dir ./filings
"""

import argparse
from pathlib import Path
from datetime import datetime
from filing_downloader import FilingDownloader


CURRENT_DIR = Path(__file__).parent
# --------------------------------------------------------------------------- #
# Command-line arguments
# --------------------------------------------------------------------------- #
now = datetime.now()
parser = argparse.ArgumentParser(description="Download filings for a given ticker and save them to a directory.")
parser.add_argument(
    "--start-year",
    type=int,
    default=now.year - 5,
    help="Fiscal year to start downloading from",
)
parser.add_argument(
    "--end-year",
    type=int,
    default=now.year - 1,
    help="Fiscal year to end downloading at",
)
parser.add_argument(
    "--ticker",
    type=str,
    default="AAPL",
    help="Ticker to download filings for",
)
parser.add_argument(
    "--output-dir",
    type=str,
    default=str(CURRENT_DIR / "output"),
    help="Output directory",
)

args = parser.parse_args()
START_YEAR = args.start_year
END_YEAR = args.end_year
TICKER = args.ticker
OUTPUT_DIR = args.output_dir

# Create output directory if it doesn't exist
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

# Download filings
if __name__ == "__main__":
    downloader = FilingDownloader(TICKER, START_YEAR, END_YEAR, str(CURRENT_DIR / OUTPUT_DIR))
    downloader.download_filings()
