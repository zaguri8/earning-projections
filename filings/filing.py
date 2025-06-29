import requests


HEADERS = {"User-Agent": "nadavavnon@gmail.com"}
URL = "https://www.sec.gov/files/company_tickers.json"

def cik_url(ticker: str) -> str:
    """
        Get the URL for the company facts for a given ticker.
        Args:
            ticker: The ticker of the company.
        Returns:
            The URL for the company facts.
    """
    return f"https://data.sec.gov/api/xbrl/companyfacts/CIK{ticker}.json"

class Filing:
    """
    A class to download and parse the 10-K filing for a given ticker and year.
    """
    def __init__(self, ticker: str, year: int):
        self.ticker = ticker
        self.year = year
        self.flat = None
        self.year_10k = None


    def ticker_to_cik(self, ticker: str) -> str:
        """
        Get the 10-digit zero-padded CIK for a given ticker (e.g., 'AAPL' → '0000320193').
        """
        
        r = requests.get(URL, headers=HEADERS)
        r.raise_for_status()
        data = r.json()

        ticker = ticker.upper()

        for entry in data.values():
            if entry["ticker"].upper() == ticker:
                return str(entry["cik_str"]).zfill(10)
        
        raise ValueError(f"Ticker '{ticker}' not found in SEC mapping.")


    def download_filing(self):
        if self.flat is not None:
            return
        
        CIK = self.ticker_to_cik(self.ticker)
        URL = cik_url(CIK)
        # --------------------------------------------------------------------------- #
        # Download the companyfacts JSON
        # --------------------------------------------------------------------------- #
        resp = requests.get(URL, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        # --------------------------------------------------------------------------- #
        # Extract US-GAAP 10-K facts for the chosen fiscal year
        # --------------------------------------------------------------------------- #
        facts = data.get("facts", {}).get("us-gaap", {})

        year_10k = {}  # concept → {"value": ..., "filed": ...}

        for concept, cdata in facts.items():
            for unit_entries in cdata.get("units", {}).values():  # walk USD, EUR, etc.
                for e in unit_entries:
                    if (
                        e.get("form") == "10-K"    # keep only 10-K filings
                        and e.get("fy") == self.year    # … for the target fiscal year
                        and "val" in e
                    ):
                        # Keep the newest 'filed' date if duplicates exist
                        rec = year_10k.get(concept)
                        if rec is None or e["filed"] > rec["filed"]:
                            year_10k[concept] = {"value": e["val"], "filed": e["filed"]}

        # Flatten to concept → value
        flat = {k: v["value"] for k, v in year_10k.items()}
        self.flat = flat
        self.year_10k = year_10k