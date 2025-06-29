from pathlib import Path
import json
from filing import Filing


DEFAULT_OUTPUT_DIR = Path(__file__).parent / "output"

class FilingDownloader:
    """
    A class to download and parse the 10-K filing for a given ticker and year.
    """
    def __init__(self, ticker: str, start_year: int, end_year: int, output_dir: str = DEFAULT_OUTPUT_DIR):
        self.ticker = ticker
        self.start_year = start_year
        self.end_year = end_year
        self.output_dir = output_dir
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        self.filings = []

    def download_filings(self):
        """
        Download the 10-K filings for the given ticker and year.
        """
        for year in range(self.start_year, self.end_year + 1):
            print(f"Downloading {self.ticker} {year} 10-K")
            filing = Filing(self.ticker, year)
            filing.download_filing()
            self.filings.append(filing)
            self.write_to_disk(filing.flat, self.ticker, year, self.output_dir)

    def write_to_disk(self, flat: dict | None, ticker: str, year: int, output_dir: str):
        """
        Write the 10-K filing to disk.
        """
        if flat is None:
            return
        outfile = Path(f"{output_dir}/{ticker}_{year}.json")
        with outfile.open("w", encoding="utf-8") as f:
            json.dump(flat, f, indent=2)

        print(f"✔  Saved {len(flat):,} 10-K facts to {outfile.resolve()}")
