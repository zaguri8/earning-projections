"""Fixed SEC 10-K parser that properly handles XBRL-to-JSON structure"""

import os, json, datetime
from pathlib import Path
from typing import Dict, Tuple, Optional, Any

import pandas as pd
from tqdm import tqdm

API_KEY = os.getenv("SEC_API_KEY") or "YOUR_API_KEY"
CURRENT_DIR = Path(__file__).parent
DEBUG = True

def debug_print(msg):
    if DEBUG:
        print(f"[DEBUG] {msg}")

# -------------------------------------------------------------------- #
#  Lazy SEC‑API imports
# -------------------------------------------------------------------- #
def _query_api():
    from sec_api import QueryApi
    return QueryApi(API_KEY)

def _xbrl_api():
    from sec_api import XbrlApi
    return XbrlApi(API_KEY)

# -------------------------------------------------------------------- #
#  Alias map
# -------------------------------------------------------------------- #
ALIAS: Dict[str, list[str]] = {
    "Revenue": [
        "Revenue", "Revenues", "SalesRevenueNet", "SalesRevenueGoodsNet", "NetSales",
        "RevenueFromContractWithCustomerExcludingAssessedTax",
        "TotalRevenuesAndOtherIncome", "RevenueFromContractWithCustomerIncludingAssessedTax"
    ],
    "COGS": [
        "CostOfGoodsSold", "CostOfSales", "CostOfGoodsAndServicesSold",
        "CostOfRevenue", "CostsAndExpenses",
        "CostOfGoodsAndServicesSoldExcludingDepreciationDepletionAndAmortization"
    ],
    "GrossProfit": [
        "GrossProfit", "GrossMargin", "GrossIncome"
    ],
    "OperatingIncome": [
        "OperatingIncome", "OperatingIncomeLoss", "IncomeLossFromOperations"
    ],
    "NetIncome": [
        "NetIncome", "NetIncomeLoss", "ProfitLoss", "NetEarnings", "NetEarningsLoss"
    ],
    "EPS": [
        "EarningsPerShareDiluted", "EarningsPerShareBasicAndDiluted", "EarningsPerShareBasic"
    ],
    "SharesDiluted": [
        "WeightedAverageNumberOfDilutedSharesOutstanding",
        "WeightedAverageNumberOfSharesOutstandingDiluted",
        "WeightedAverageSharesOutstandingDiluted"
    ],
    "CFO": [
        "NetCashProvidedByUsedInOperatingActivities",
        "NetCashProvidedByOperatingActivities"
    ],
    "CapEx": [
        "PaymentsToAcquirePropertyPlantAndEquipment",
        "PaymentsForPropertyPlantAndEquipment",
        "CapitalExpendituresIncurredButNotYetPaid"
    ],
    "R&D": [
        "ResearchAndDevelopmentExpense", "ResearchAndDevelopmentExpenseExcludingAcquiredInProcess",
        "ResearchDevelopmentAndRelatedExpenses"
    ],
    "SG&A": [
        "SellingGeneralAndAdministrativeExpense", "SellingAndMarketingExpense", "GeneralAndAdministrativeExpense"
    ],
}

# -------------------------------------------------------------------- #
def _norm(val: Any) -> Optional[float]:
    """Normalize value to float, handling XBRL decimal format"""
    if val is None:
        return None
    if isinstance(val, (int, float)):
        return float(val)
    if isinstance(val, dict):
        if "value" in val:
            base = float(val["value"])
            dec = int(val.get("decimals", 0))
            return base * (10 ** dec)
        elif "val" in val:  # Alternative format
            base = float(val["val"])
            dec = int(val.get("decimals", 0))
            return base * (10 ** dec)
    try:
        return float(val)
    except Exception:
        return None

def find_annual_value(data_list: list, target_year: int) -> Optional[float]:
    """Find the annual value from a list of time-period data points"""
    if not isinstance(data_list, list):
        return None
    
    for item in data_list:
        if not isinstance(item, dict):
            continue
            
        # Check if this is annual data (12 months duration)
        period = item.get("period", {})
        if isinstance(period, dict):
            start_date = period.get("startDate", "")
            end_date = period.get("endDate", "")
            
            # Parse year from end date
            if end_date:
                try:
                    year = int(end_date[:4])
                    if year == target_year:
                        # Check if it's annual (roughly 12 months)
                        if start_date:
                            start_year = int(start_date[:4])
                            if year - start_year <= 1:  # Annual period
                                value = _norm(item)
                                if value is not None:
                                    debug_print(f"Found annual value for {target_year}: {value}")
                                    return value
                except (ValueError, TypeError):
                    continue
    
    return None

def search_in_section(section_data: Any, aliases: list, target_year: int) -> Optional[float]:
    """Search for financial data within a specific section"""
    if not section_data:
        return None
    
    # Direct alias match in section
    for alias in aliases:
        if isinstance(section_data, dict) and alias in section_data:
            data = section_data[alias]
            if isinstance(data, list):
                value = find_annual_value(data, target_year)
                if value is not None:
                    return value
            elif isinstance(data, dict):
                value = _norm(data)
                if value is not None:
                    return value
    
    # Recursive search in nested structures
    if isinstance(section_data, dict):
        for key, value in section_data.items():
            if key in aliases:
                if isinstance(value, list):
                    result = find_annual_value(value, target_year)
                    if result is not None:
                        return result
                elif isinstance(value, dict):
                    result = _norm(value)
                    if result is not None:
                        return result
            elif isinstance(value, (dict, list)):
                result = search_in_section(value, aliases, target_year)
                if result is not None:
                    return result
    elif isinstance(section_data, list):
        for item in section_data:
            result = search_in_section(item, aliases, target_year)
            if result is not None:
                return result
    
    return None


def _extract_from_xbrl_flat(blob: dict, target_year: int) -> Dict[str, Optional[float]]:
    """Extract financial metrics from SEC-API/flat XBRL JSON structure."""
    debug_print(f"Extracting metrics for year {target_year}")
    debug_print(f"XBRL blob keys: {list(blob.keys())[:20]}")
    
    results = {}

    for metric_name, aliases in ALIAS.items():
        found_value = None
        # Try all aliases as direct keys
        for alias in aliases:
            if alias in blob:
                data_list = blob[alias]
                val = find_annual_value(data_list, target_year)
                if val is not None:
                    found_value = val
                    break
            for key in blob:
                if key.endswith(":" + alias):
                    data_list = blob[key]
                    val = find_annual_value(data_list, target_year)
                    if val is not None:
                        found_value = val
                        break
            if found_value is not None:
                break
        results[metric_name] = found_value
        debug_print(f"Final value for {metric_name}: {found_value}")

    # Derived metrics
    if results["Revenue"] and results["COGS"]:
        results["GrossProfit"] = results["Revenue"] - results["COGS"]
        results["GrossMargin"] = results["GrossProfit"] / results["Revenue"]
    if results["OperatingIncome"] and results["Revenue"]:
        results["OperatingMargin"] = results["OperatingIncome"] / results["Revenue"]
    if results["NetIncome"] and results["Revenue"]:
        results["NetMargin"] = results["NetIncome"] / results["Revenue"]
    if results["CFO"] is not None and results["CapEx"] is not None:
        results["FCF"] = results["CFO"] - abs(results["CapEx"])
        if results["Revenue"]:
            results["FCFMargin"] = results["FCF"] / results["Revenue"]

    return results


def _extract_from_xbrl(blob: dict, target_year: int) -> Dict[str, Optional[float]]:
    """Extract financial metrics from XBRL JSON structure"""
    debug_print(f"Extracting metrics for year {target_year}")
    debug_print(f"XBRL blob keys: {list(blob.keys())}")
    
    results = {}
    
    # Define which sections to search for each metric type
    SECTION_PRIORITIES = {
        "Revenue": ["StatementsOfIncome", "Revenue", "RevenueTables"],
        "COGS": ["StatementsOfIncome"],
        "NetIncome": ["StatementsOfIncome"],
        "OperatingIncome": ["StatementsOfIncome"],
        "GrossProfit": ["StatementsOfIncome"],
        "EPS": ["StatementsOfIncome", "EarningsPerShare", "EarningsPerShareTables"],
        "SharesDiluted": ["EarningsPerShare", "EarningsPerShareTables"],
        "CFO": ["StatementsOfCashFlows"],
        "CapEx": ["StatementsOfCashFlows"],
        "R&D": ["StatementsOfIncome"],
        "SG&A": ["StatementsOfIncome"],
    }
    
    for metric_name, aliases in ALIAS.items():
        debug_print(f"\nSearching for {metric_name} with aliases: {aliases}")
        
        found_value = None
        
        # Search in priority sections first
        priority_sections = SECTION_PRIORITIES.get(metric_name, ["StatementsOfIncome", "StatementsOfCashFlows"])
        
        for section_name in priority_sections:
            if section_name in blob:
                debug_print(f"Searching in section: {section_name}")
                section_data = blob[section_name]
                found_value = search_in_section(section_data, aliases, target_year)
                if found_value is not None:
                    debug_print(f"Found {metric_name} in {section_name}: {found_value}")
                    break
        
        # If not found in priority sections, search all sections
        if found_value is None:
            debug_print(f"Not found in priority sections, searching all sections...")
            for section_name, section_data in blob.items():
                if section_name.startswith(('Statements', 'Revenue', 'EarningsPerShare', 'CashFlow')):
                    found_value = search_in_section(section_data, aliases, target_year)
                    if found_value is not None:
                        debug_print(f"Found {metric_name} in {section_name}: {found_value}")
                        break
        
        results[metric_name] = found_value
        debug_print(f"Final value for {metric_name}: {found_value}")
    
    # Calculate derived metrics
    if results["Revenue"] and results["COGS"]:
        results["GrossProfit"] = results["Revenue"] - results["COGS"]
        results["GrossMargin"] = results["GrossProfit"] / results["Revenue"]
    
    if results["OperatingIncome"] and results["Revenue"]:
        results["OperatingMargin"] = results["OperatingIncome"] / results["Revenue"]
    
    if results["NetIncome"] and results["Revenue"]:
        results["NetMargin"] = results["NetIncome"] / results["Revenue"]
    
    if results["CFO"] is not None and results["CapEx"] is not None:
        results["FCF"] = results["CFO"] - abs(results["CapEx"])
        if results["Revenue"]:
            results["FCFMargin"] = results["FCF"] / results["Revenue"]
    
    return results

# -------------------------------------------------------------------- #
#  File Loading Functions
# -------------------------------------------------------------------- #
def _load_from_file(ticker: str, year: int, input_dir: str = "./input") -> dict:
    """Load XBRL JSON from local file"""
    input_path = Path(input_dir)
    
    # Try multiple possible filename formats
    possible_files = [
        f"{ticker}_{year}.json",
        f"{ticker.upper()}_{year}.json",
        f"{ticker.lower()}_{year}.json",
        f"{ticker}_{year}_xbrl.json",
        f"{ticker.upper()}_{year}_xbrl.json",
        f"{ticker.lower()}_{year}_xbrl.json",
    ]
    
    for filename in possible_files:
        file_path = input_path / filename
        if file_path.exists():
            debug_print(f"Loading from file: {file_path}")
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    
    # If no standard format found, look for any JSON file containing ticker and year
    for json_file in input_path.glob("*.json"):
        if ticker.upper() in json_file.name.upper() and str(year) in json_file.name:
            debug_print(f"Loading from file: {json_file}")
            with open(json_file, 'r', encoding='utf-8') as f:
                return json.load(f)
    
    raise FileNotFoundError(f"No XBRL JSON file found for {ticker} {year} in {input_path}. "
                          f"Expected formats: {', '.join(possible_files)}")

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
#  SEC helpers (modified to support file loading)
# -------------------------------------------------------------------- #
def _latest_year(tkr: str, from_files: bool = False, input_dir: str = "./input") -> int:
    """
    Get the latest year for a given ticker.
    """
    if from_files:
        available = _list_available_files(input_dir)
        if tkr.upper() not in available:
            raise ValueError(f"No files found for ticker {tkr} in {input_dir}")
        return max(available[tkr.upper()])
    else:
        q = {"query": f'ticker:{tkr} AND formType:"10-K"', "from":0, "size":1,
             "sort":[{"filedAt":{"order":"desc"}}]}
        return int(_query_api().get_filings(q)["filings"][0]["filedAt"][:4])

def _k_url(tkr: str, yr: int) -> str:
    """
    Get the URL for a given ticker and year.
    """
    q = {"query": f'ticker:{tkr} AND formType:"10-K" AND filedAt:[{yr}-01-01 TO {yr}-12-31]',
         "from":0,"size":1,"sort":[{"filedAt":{"order":"desc"}}]}
    fl = _query_api().get_filings(q)["filings"]
    if not fl: raise ValueError(f"No 10-K for {tkr} {yr}")
    return fl[0]["linkToFilingDetails"]

def _fetch_json(tkr: str, yr: int, from_files: bool = False, input_dir: str = "./input") -> dict:
    """
    Fetch the JSON for a given ticker and year.
    """
    if from_files:
        return _load_from_file(tkr, yr, input_dir)
    else:
        return _xbrl_api().xbrl_to_json(htm_url=_k_url(tkr, yr))

def _history(tkr: str, back: int, current_year: int | None = None, from_files: bool = False, input_dir: str = "./input") -> pd.DataFrame:
    """Get historical data going back 'back' years from current_year-1 (projections always start at current_year)"""
    if current_year is None:
        current_year = _latest_year(tkr, from_files, input_dir)
    end_year = current_year - 1
    start_year = end_year - back + 1
    if from_files:
        available = _list_available_files(input_dir)
        ticker_upper = tkr.upper()
        if ticker_upper not in available:
            raise ValueError(f"No files found for ticker {tkr} in {input_dir}")
        available_years = available[ticker_upper]
        requested_years = list(range(start_year, end_year + 1))
        missing_years = [y for y in requested_years if y not in available_years]
        if missing_years:
            print(f"Warning: Missing files for years {missing_years}")
            print(f"Available years for {tkr}: {sorted(available_years)}")
        years_to_process = [y for y in requested_years if y in available_years]
    else:
        years_to_process = list(range(start_year, end_year + 1))
    rows = {}
    for yr in tqdm(years_to_process, desc=f"{tkr} 10-Ks"):
        try:
            blob = _fetch_json(tkr, yr, from_files, input_dir)
            if from_files:
                # Use flat extractor if all values are numbers (flat structure)
                if all(isinstance(v, (int, float)) for v in blob.values()):
                    metrics = extract_from_simple_flat(blob)
                else:
                    metrics = _extract_from_xbrl_flat(blob, yr)
            else:
                metrics = _extract_from_xbrl(blob, yr)
            for k, v in metrics.items():
                rows.setdefault(k, {})[yr] = v
        except Exception as e:
            print(f"Error processing {tkr} {yr}: {e}")
            continue
    if not rows:
        raise ValueError(f"No data could be extracted for {tkr}")
    df = pd.DataFrame(rows).T
    df = df[sorted(df.columns)]
    df.columns = df.columns.astype(str)
    return df


# -------------------------------------------------------------------- #
def _proj(df: pd.DataFrame, start_year: int, num_years: int, ass: Dict[str, Dict[str, float]], s: str) -> pd.DataFrame:
    """
    Project from start_year for num_years, even if start_year is not in df.
    First projection year always uses the last available hist year as base if start_year is missing in df.
    """
    p = df.copy()
    last_hist_year = p.columns[-1]
    for i in range(num_years):
        y = str(start_year + i)
        col = {}
        # For first projection year, use last hist year if start_year not in df
        if y == str(start_year):
            prev_year = last_hist_year if y not in p.columns else y
        else:
            prev_year = str(start_year + i - 1)
        for m in p.index:
            base = p.at[m, prev_year]
            if pd.isna(base):
                col[m] = None
                continue
            g = ass.get(m, {}).get(s, ass.get("revenue", {}).get(s, 0))
            col[m] = base * (1 + g)
        p[y] = pd.Series(col)
    # Ensure columns are sorted by year (hist + projections in order)
    p = p[p.columns.sort_values(key=lambda x: [int(c) if c.isdigit() else 9999 for c in p.columns])]
    return p


def build_projections(ticker:str, years_back:int=5, current_year:int=2025, proj_years:int=5,
                      growth:Optional[Dict[str,Dict[str,float]]]={"revenue":{"bear":0.02,"base":0.05,"bull":0.09}},
                      out_dir:Optional[str]=None, from_files:bool=False, input_dir:str="./input")->Tuple[pd.DataFrame,pd.DataFrame,pd.DataFrame]:
    """
    Build projections starting from current_year for proj_years
    
    Args:
        ticker: Stock ticker symbol
        years_back: Number of historical years to fetch (from current_year-1 backwards)
        current_year: Base year for projections (default 2025)
        proj_years: Number of years to project forward (default 5 for current_year-current_year+4)
        growth: Growth rate assumptions
        out_dir: Output directory
        from_files: Whether to load from local files instead of SEC API
        input_dir: Directory containing input files when from_files=True
    """
    
    if from_files:
        print(f"Loading data from files in: {input_dir}")
        available = _list_available_files(input_dir)
        if ticker.upper() in available:
            print(ticker.upper())
            print(available)
            print(f"Available years for {ticker}: {sorted(available[ticker.upper()])}")
    
    # Get historical data from (current_year - years_back) to (current_year - 1)
    # Example: if current_year=2025 and years_back=5, get 2020-2024
    hist = _history(ticker, years_back, current_year, from_files, input_dir)
    
    
    # Project from current_year for proj_years
    # Example: if current_year=2025 and proj_years=5, project 2025-2029
    bear = _proj(hist, current_year, proj_years, growth, "bear")
    base = _proj(hist, current_year, proj_years, growth, "base")
    bull = _proj(hist, current_year, proj_years, growth, "bull")
    
    directory = Path(out_dir or f"./{ticker}_model")
    directory.mkdir(exist_ok=True, parents=True)
    print("Writing CSVs to:", directory.resolve())
    hist.to_csv(directory/f"{ticker}_historical.csv")
    bear.to_csv(directory/f"{ticker}_bear.csv")
    base.to_csv(directory/f"{ticker}_base.csv")
    bull.to_csv(directory/f"{ticker}_bull.csv")
    
    return hist, (bear, base, bull)


def extract_from_simple_flat(blob: dict) -> Dict[str, Optional[float]]:
    """Extract metrics from a flat dict with concept → value (no time info)"""
    results = {}
    for metric, aliases in ALIAS.items():
        for alias in aliases:
            if alias in blob:
                results[metric] = blob[alias]
                break
        else:
            results[metric] = None  # not found

    # Derived metrics
    if results["Revenue"] and results["COGS"]:
        results["GrossProfit"] = results["Revenue"] - results["COGS"]
        results["GrossMargin"] = results["GrossProfit"] / results["Revenue"]
    if results["OperatingIncome"] and results["Revenue"]:
        results["OperatingMargin"] = results["OperatingIncome"] / results["Revenue"]
    if results["NetIncome"] and results["Revenue"]:
        results["NetMargin"] = results["NetIncome"] / results["Revenue"]
    if results["CFO"] is not None and results["CapEx"] is not None:
        results["FCF"] = results["CFO"] - abs(results["CapEx"])
        if results["Revenue"]:
            results["FCFMargin"] = results["FCF"] / results["Revenue"]
    return results

# Test function
def test_single_year(ticker: str, year: int, from_files: bool = False, input_dir: str = "./input"):
    """Test extraction for a single year"""
    debug_print(f"Testing {ticker} for year {year}")
    
    try:
        blob = _fetch_json(ticker, year, from_files, input_dir)
        debug_print(f"Available sections: {list(blob.keys())}")
        
        # Show what's in key sections
        if "StatementsOfIncome" in blob:
            income_stmt = blob["StatementsOfIncome"]
            debug_print(f"StatementsOfIncome keys: {list(income_stmt.keys())[:20] if isinstance(income_stmt, dict) else 'Not a dict'}")
        
        if "Revenue" in blob:
            revenue_section = blob["Revenue"] 
            debug_print(f"Revenue section keys: {list(revenue_section.keys())[:20] if isinstance(revenue_section, dict) else 'Not a dict'}")
        
        if "StatementsOfCashFlows" in blob:
            cf_stmt = blob["StatementsOfCashFlows"]
            debug_print(f"StatementsOfCashFlows keys: {list(cf_stmt.keys())[:20] if isinstance(cf_stmt, dict) else 'Not a dict'}")
        
        metrics = extract_from_simple_flat(blob)
        
        print(f"\nResults for {ticker} {year}:")
        for k, v in metrics.items():
            if v is not None:
                if isinstance(v, float) and abs(v) > 1000000:
                    print(f"  {k}: ${v:,.0f}")
                else:
                    print(f"  {k}: {v}")
            else:
                print(f"  {k}: None")
                
        return metrics
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

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--ticker", type=str, default="AAPL", help="Ticker to run")
    p.add_argument("--year", type=int, help="Test specific year")
    p.add_argument("--years_back", type=int, default=4)
    now = datetime.datetime.now()
    p.add_argument("--current_year", type=int, default=now.year, help="Base year for projections (default: current year)")
    p.add_argument("--proj_years", type=int, default=5, help="Number of years to project (default: 5 for current_year-proj_years)")
    p.add_argument("--growth-bear", type=float, default=0.02, help="Growth rate for bear case (default: 0.02)")
    p.add_argument("--growth-base", type=float, default=0.05, help="Growth rate for base case (default: 0.05)")
    p.add_argument("--growth-bull", type=float, default=0.09, help="Growth rate for bull case (default: 0.09)")
    p.add_argument("--out_dir", default=str(CURRENT_DIR / "output"))
    p.add_argument("--from_files", action="store_true", help="Load data from local files instead of SEC API",default=True)
    p.add_argument("--input_dir", default=str(CURRENT_DIR / "../filings/output"), help="Directory containing input JSON files")
    p.add_argument("--list_available", action="store_true", help="List available data files")
    args = p.parse_args()
    
    if args.list_available:
        list_available_data(args.input_dir)
    elif args.year:
        test_single_year(args.ticker, args.year, args.from_files, args.input_dir)
    else:
        # Run full projection
        try:
            hist, (bear, base, bull) = build_projections(
                args.ticker, args.years_back, args.current_year, args.proj_years,
                {"revenue":{"bear":args.growth_bear,"base":args.growth_base,"bull":args.growth_bull}},
                args.out_dir, args.from_files, args.input_dir
            )
            print(f"\nProjections for {args.ticker} ({args.current_year}-{args.current_year + args.proj_years - 1}):")
            print("\nBase‑case preview:")
            print(base.iloc[:5, :])         # All columns, first 5 metrics
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()