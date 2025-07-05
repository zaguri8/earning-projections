"""SEC 10-K Financial Model with Improved Computations and Scalability"""

import os, json, datetime
from pathlib import Path
from typing import Dict, Tuple, Optional, Any, List, Union
from dataclasses import dataclass, asdict
import logging

import pandas as pd
import numpy as np
from tqdm import tqdm

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

API_KEY = os.getenv("SEC_API_KEY") or "YOUR_API_KEY"
CURRENT_DIR = Path(__file__).parent
DEBUG = True

@dataclass
class ProjectionParams:
    """Parameters for financial projections"""
    revenue_growth: Dict[str, float]
    years_back: int = 5
    current_year: int = 2025
    proj_years: int = 5
    profit_margin_target: Optional[float] = 0.15
    years_to_profitability: int = 5
    margin_growth: Optional[Dict[str, float]] = None
    terminal_growth_rate: float = 0.025  # Long-term growth rate
    discount_rate: float = 0.10  # WACC approximation
    
    # New parameters
    capex_as_pct_revenue: Optional[Dict[str, float]] = None
    working_capital_change: Optional[Dict[str, float]] = None
    debt_equity_target: Optional[float] = None
    dividend_payout_ratio: Optional[float] = None
    share_buyback_pct: Optional[float] = None

@dataclass
class FinancialMetrics:
    """Structured financial metrics"""
    revenue: Optional[float] = None
    cogs: Optional[float] = None
    gross_profit: Optional[float] = None
    rd_expense: Optional[float] = None
    sga_expense: Optional[float] = None
    operating_income: Optional[float] = None
    net_income: Optional[float] = None
    eps: Optional[float] = None
    shares_diluted: Optional[float] = None
    cfo: Optional[float] = None
    capex: Optional[float] = None
    fcf: Optional[float] = None
    
    # Additional metrics
    ebitda: Optional[float] = None
    total_debt: Optional[float] = None
    cash: Optional[float] = None
    book_value: Optional[float] = None
    working_capital: Optional[float] = None
    
    # Ratios
    gross_margin: Optional[float] = None
    operating_margin: Optional[float] = None
    net_margin: Optional[float] = None
    fcf_margin: Optional[float] = None
    roe: Optional[float] = None
    roa: Optional[float] = None
    debt_to_equity: Optional[float] = None
    
    def calculate_derived_metrics(self):
        """Calculate derived metrics from base metrics"""
        if self.revenue and self.cogs:
            self.gross_profit = self.revenue - self.cogs
        
        if self.revenue and self.revenue > 0:
            if self.gross_profit:
                self.gross_margin = self.gross_profit / self.revenue
            if self.operating_income:
                self.operating_margin = self.operating_income / self.revenue
            if self.net_income:
                self.net_margin = self.net_income / self.revenue
            if self.fcf:
                self.fcf_margin = self.fcf / self.revenue
        
        if self.cfo and self.capex:
            self.fcf = self.cfo - abs(self.capex)
        
        if self.net_income and self.shares_diluted and self.shares_diluted > 0:
            self.eps = self.net_income / self.shares_diluted

class FinancialModel:
    """Financial model with improved computations and scalability"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or API_KEY
        self.alias_map = self._init_alias_map()
        self.cache = {}
        
    def _init_alias_map(self) -> Dict[str, List[str]]:
        """Initialize comprehensive alias mapping"""
        return {
            "Revenue": [
                "Revenue", "Revenues", "SalesRevenueNet", "SalesRevenueGoodsNet", "NetSales",
                "RevenueFromContractWithCustomerExcludingAssessedTax",
                "TotalRevenuesAndOtherIncome", "RevenueFromContractWithCustomerIncludingAssessedTax",
                "TotalRevenue", "TotalRevenueNet", "RevenueNet"
            ],
            "COGS": [
                "CostOfGoodsSold", "CostOfSales", "CostOfGoodsAndServicesSold",
                "CostOfRevenue", "CostsAndExpenses",
                "CostOfGoodsAndServicesSoldExcludingDepreciationDepletionAndAmortization",
                "CostOfGoodsSoldExcludingDepreciationDepletionAndAmortization"
            ],
            "R&D": [
                "ResearchAndDevelopmentExpense", "ResearchAndDevelopmentExpenseExcludingAcquiredInProcess",
                "ResearchDevelopmentAndRelatedExpenses", "ResearchAndDevelopmentExpenseIncludingAcquiredInProcessCost"
            ],
            "SG&A": [
                "SellingGeneralAndAdministrativeExpense", "SellingAndMarketingExpense", 
                "GeneralAndAdministrativeExpense", "SellingGeneralAndAdministrativeExpenseExcludingAcquiredInProcess"
            ],
            "OperatingIncome": [
                "OperatingIncome", "OperatingIncomeLoss", "IncomeLossFromOperations",
                "OperatingIncomeFromSegments", "OperatingIncomeLossExcludingRestructuring"
            ],
            "NetIncome": [
                "NetIncome", "NetIncomeLoss", "ProfitLoss", "NetEarnings", "NetEarningsLoss",
                "NetIncomeLossAttributableToParent", "NetIncomeLossAvailableToCommonStockholdersBasic"
            ],
            "EPS": [
                "EarningsPerShareDiluted", "EarningsPerShareBasicAndDiluted", "EarningsPerShareBasic",
                "EarningsPerShareDilutedExtraordinaryItems"
            ],
            "SharesDiluted": [
                "WeightedAverageNumberOfDilutedSharesOutstanding",
                "WeightedAverageNumberOfSharesOutstandingDiluted",
                "WeightedAverageSharesOutstandingDiluted", "CommonStockSharesOutstanding"
            ],
            "CFO": [
                "NetCashProvidedByUsedInOperatingActivities",
                "NetCashProvidedByOperatingActivities", "CashFlowFromOperatingActivities"
            ],
            "CapEx": [
                "PaymentsToAcquirePropertyPlantAndEquipment",
                "PaymentsForPropertyPlantAndEquipment",
                "CapitalExpendituresIncurredButNotYetPaid", "CapitalExpenditures"
            ],
            "TotalDebt": [
                "DebtCurrent", "DebtNoncurrent", "TotalDebt", "DebtAndCapitalLeaseObligations",
                "LongTermDebtAndCapitalLeaseObligations"
            ],
            "Cash": [
                "CashAndCashEquivalents", "CashAndShortTermInvestments", "Cash"
            ],
            "BookValue": [
                "StockholdersEquity", "ShareholdersEquity", "BookValuePerShare"
            ]
        }
    
    def _normalize_value(self, val: Any) -> Optional[float]:
        """Value normalization with better error handling"""
        if val is None:
            return None
        
        if isinstance(val, (int, float)):
            return float(val)
        
        if isinstance(val, dict):
            if "value" in val:
                base = float(val["value"])
                dec = int(val.get("decimals", 0))
                return base * (10 ** dec)
            elif "val" in val:
                base = float(val["val"])
                dec = int(val.get("decimals", 0))
                return base * (10 ** dec)
        
        if isinstance(val, str):
            # Handle string representations of numbers
            try:
                # Remove common formatting
                clean_val = val.replace(',', '').replace('$', '').replace('(', '-').replace(')', '')
                return float(clean_val)
            except ValueError:
                pass
        
        try:
            return float(val)
        except (ValueError, TypeError):
            return None
    
    def _find_annual_value(self, data_list: List[Any], target_year: int) -> Optional[float]:
        """Annual value finder with better date parsing"""
        if not isinstance(data_list, list):
            return None
        
        candidates = []
        
        for item in data_list:
            if not isinstance(item, dict):
                continue
            
            period = item.get("period", {})
            if not isinstance(period, dict):
                continue
            
            start_date = period.get("startDate", "")
            end_date = period.get("endDate", "")
            
            if not end_date:
                continue
            
            try:
                # Parse dates more robustly
                end_year = int(end_date[:4])
                if end_year != target_year:
                    continue
                
                # Calculate period length
                if start_date:
                    start_year = int(start_date[:4])
                    period_length = end_year - start_year
                    
                    # Prefer annual data (11-13 months to account for fiscal year variations)
                    if period_length <= 1:
                        value = self._normalize_value(item)
                        if value is not None:
                            candidates.append((value, period_length, end_date))
                
            except (ValueError, TypeError):
                continue
        
        if not candidates:
            return None
        
        # Sort by period length (prefer annual), then by end date (most recent)
        candidates.sort(key=lambda x: (x[1], x[2]), reverse=True)
        return candidates[0][0]
    
    def extract_metrics_from_xbrl(self, xbrl_data: Dict[str, Any], target_year: int) -> FinancialMetrics:
        """Extract financial metrics from XBRL data with improved logic"""
        metrics = FinancialMetrics()
        
        # Check if this is flat data (all values are numbers)
        if all(isinstance(v, (int, float)) for v in xbrl_data.values()):
            # Handle flat data structure
            return self._extract_from_flat_data(xbrl_data)
        
        # Define section priorities for different metrics
        section_priorities = {
            "Revenue": ["StatementsOfIncome", "Revenue", "StatementsOfOperations"],
            "COGS": ["StatementsOfIncome", "StatementsOfOperations"],
            "NetIncome": ["StatementsOfIncome", "StatementsOfOperations"],
            "CFO": ["StatementsOfCashFlows", "CashFlowStatement"],
            "CapEx": ["StatementsOfCashFlows", "CashFlowStatement"],
            "TotalDebt": ["BalanceSheet", "StatementsOfFinancialPosition"],
            "Cash": ["BalanceSheet", "StatementsOfFinancialPosition"],
            "BookValue": ["BalanceSheet", "StatementsOfFinancialPosition"]
        }
        
        # Extract metrics using improved search
        for metric_name, aliases in self.alias_map.items():
            value = self._search_in_sections(xbrl_data, aliases, target_year, 
                                           section_priorities.get(metric_name, []))
            setattr(metrics, metric_name.lower().replace('&', ''), value)
        
        # Calculate derived metrics
        metrics.calculate_derived_metrics()
        
        return metrics
    
    def _extract_from_flat_data(self, flat_data: Dict[str, Any]) -> FinancialMetrics:
        """Extract metrics from flat data structure"""
        metrics = FinancialMetrics()
        
        # Map flat data keys to metrics
        for metric_name, aliases in self.alias_map.items():
            for alias in aliases:
                if alias in flat_data:
                    value = self._normalize_value(flat_data[alias])
                    setattr(metrics, metric_name.lower().replace('&', ''), value)
                    logger.info(f"Extracted {metric_name}: {value} from {alias}")
                    break
            else:
                logger.warning(f"Could not find any alias for {metric_name}: {aliases}")
        
        # Calculate derived metrics
        metrics.calculate_derived_metrics()
        
        return metrics
    
    def _search_in_sections(self, data: Dict[str, Any], aliases: List[str], 
                          target_year: int, priority_sections: List[str]) -> Optional[float]:
        """Search for metric in prioritized sections"""
        # First, search in priority sections
        for section_name in priority_sections:
            if section_name in data:
                value = self._search_in_section(data[section_name], aliases, target_year)
                if value is not None:
                    return value
        
        # If not found, search in all sections
        for section_name, section_data in data.items():
            if section_name.startswith(('Statements', 'Revenue', 'EarningsPerShare', 'CashFlow')):
                value = self._search_in_section(section_data, aliases, target_year)
                if value is not None:
                    return value
        
        return None
    
    def _search_in_section(self, section_data: Any, aliases: List[str], target_year: int) -> Optional[float]:
        """Recursive search within a section"""
        if not section_data:
            return None
        
        # Direct alias match
        for alias in aliases:
            if isinstance(section_data, dict) and alias in section_data:
                data = section_data[alias]
                if isinstance(data, list):
                    value = self._find_annual_value(data, target_year)
                    if value is not None:
                        return value
                else:
                    value = self._normalize_value(data)
                    if value is not None:
                        return value
        
        # Recursive search
        if isinstance(section_data, dict):
            for key, value in section_data.items():
                if key in aliases:
                    if isinstance(value, list):
                        result = self._find_annual_value(value, target_year)
                        if result is not None:
                            return result
                    else:
                        result = self._normalize_value(value)
                        if result is not None:
                            return result
                elif isinstance(value, (dict, list)):
                    result = self._search_in_section(value, aliases, target_year)
                    if result is not None:
                        return result
        
        elif isinstance(section_data, list):
            for item in section_data:
                result = self._search_in_section(item, aliases, target_year)
                if result is not None:
                    return result
        
        return None
    
    def build_projections(self, ticker: str, params: ProjectionParams, 
                                 from_files: bool = False, input_dir: str = "./input") -> Dict[str, pd.DataFrame]:
        """Build projections with improved financial modeling"""
        
        # Get historical data
        historical_data = self._get_historical_data(ticker, params, from_files, input_dir)
        
        # Build projections for each scenario
        projections = {}
        for scenario in ['bear', 'base', 'bull']:
            projections[scenario] = self._project_scenario(
                historical_data, params, scenario
            )
        
        return {
            'historical': historical_data,
            'bear': projections['bear'],
            'base': projections['base'],
            'bull': projections['bull']
        }
    
    def _get_historical_data(self, ticker: str, params: ProjectionParams, 
                           from_files: bool, input_dir: str) -> pd.DataFrame:
        """Get historical financial data"""
        end_year = params.current_year - 1
        start_year = end_year - params.years_back + 1
        
        historical_metrics = {}
        
        for year in range(start_year, end_year + 1):
            try:
                if from_files:
                    xbrl_data = self._load_from_file(ticker, year, input_dir)
                else:
                    xbrl_data = self._fetch_from_api(ticker, year)
                
                metrics = self.extract_metrics_from_xbrl(xbrl_data, year)
                metrics_dict = asdict(metrics)
                
                # MINIMAL FIX: Ensure shares_diluted is present in the dict if it was extracted
                if hasattr(metrics, 'sharesdiluted') and getattr(metrics, 'sharesdiluted') is not None:
                    metrics_dict['shares_diluted'] = getattr(metrics, 'sharesdiluted')
                
                historical_metrics[year] = metrics_dict
                
            except Exception as e:
                logger.warning(f"Error processing {ticker} {year}: {e}")
                continue
        
        # Convert to DataFrame
        df = pd.DataFrame(historical_metrics).T
        df.index.name = 'Year'
        
        return df
    
    def _infer_profitability_assumptions(self, revenue_growth: float, historical_data: pd.DataFrame) -> Tuple[Optional[float], int]:
        """
        Infer profitability assumptions from growth rate and historical data
        
        Args:
            revenue_growth: Annual revenue growth rate
            historical_data: Historical financial data
            
        Returns:
            Tuple of (target_profit_margin, years_to_profitability)
        """
        # Check if company is currently profitable
        last_year_data = historical_data.iloc[-1]
        current_net_income = last_year_data.get('net_income', 0)
        current_revenue = last_year_data.get('revenue', 1)
        
        # If already profitable, no need for profitability assumptions
        if current_net_income > 0:
            return None, 0
        
        # Infer assumptions based on growth rate
        if revenue_growth >= 0.20:  # 20%+ growth (high-growth startup)
            target_margin = 0.10  # 10% target margin
            years_to_profit = 7   # 7 years to profitability
        elif revenue_growth >= 0.15:  # 15-20% growth (growth company)
            target_margin = 0.12  # 12% target margin
            years_to_profit = 6   # 6 years to profitability
        elif revenue_growth >= 0.10:  # 10-15% growth (moderate growth)
            target_margin = 0.15  # 15% target margin
            years_to_profit = 5   # 5 years to profitability
        elif revenue_growth >= 0.05:  # 5-10% growth (mature company)
            target_margin = 0.18  # 18% target margin
            years_to_profit = 4   # 4 years to profitability
        else:  # <5% growth (declining/mature)
            target_margin = 0.20  # 20% target margin
            years_to_profit = 3   # 3 years to profitability
        
        # Adjust based on current operating margin if available
        current_op_margin = last_year_data.get('operating_margin', None)
        if current_op_margin is not None and not pd.isna(current_op_margin):
            # If already close to breakeven, reduce time to profitability
            if current_op_margin > -0.05:  # Within 5% of breakeven
                years_to_profit = max(2, years_to_profit - 2)
            elif current_op_margin > -0.10:  # Within 10% of breakeven
                years_to_profit = max(3, years_to_profit - 1)
        
        return target_margin, years_to_profit

    def _project_scenario(self, historical_data: pd.DataFrame, params: ProjectionParams, 
                         scenario: str) -> pd.DataFrame:
        """Project financials for a specific scenario with improved modeling"""
        
        # Get growth rates for this scenario
        revenue_growth = params.revenue_growth.get(scenario, 0.05)
        
        # Get last historical year data
        last_year_data = historical_data.iloc[-1].copy()
        
        # Check if company is profitable and infer assumptions if needed
        current_net_income = last_year_data.get('net_income', 0)
        is_profitable = current_net_income > 0
        
        if not is_profitable:
            # Infer profitability assumptions from growth rate
            inferred_target_margin, inferred_years = self._infer_profitability_assumptions(revenue_growth, historical_data)
            
            # Use inferred assumptions unless explicitly provided
            target_margin = params.profit_margin_target if params.profit_margin_target is not None else inferred_target_margin
            years_to_profit = params.years_to_profitability if params.years_to_profitability != 5 else inferred_years
            
            logger.info(f"Unprofitable company detected. Inferred: {target_margin:.1%} margin target, {years_to_profit} years to profitability")
        else:
            target_margin = None
            years_to_profit = 0
            logger.info("Profitable company detected. Using historical margins with growth rates.")
        
        # Initialize projection DataFrame
        projection_years = range(params.current_year, params.current_year + params.proj_years)
        projected_data = pd.DataFrame(index=projection_years, columns=historical_data.columns)
        
        # Projection logic
        for i, year in enumerate(projection_years):
            if i == 0:
                base_data = last_year_data
            else:
                base_data = projected_data.iloc[i-1]
            
            # Project revenue
            projected_revenue = base_data['revenue'] * (1 + revenue_growth) if pd.notna(base_data['revenue']) else None
            projected_data.loc[year, 'revenue'] = projected_revenue
            
            # Project expenses with more sophisticated modeling
            if projected_revenue and pd.notna(projected_revenue):
                # COGS as percentage of revenue (with efficiency improvements)
                cogs_margin = base_data['cogs'] / base_data['revenue'] if pd.notna(base_data['cogs']) and base_data['revenue'] > 0 else 0.6
                # Assume slight efficiency gains over time
                cogs_margin_improved = cogs_margin * (1 - 0.005 * i)  # 0.5% improvement per year
                projected_data.loc[year, 'cogs'] = projected_revenue * cogs_margin_improved
                
                # R&D scaling with some economies of scale
                rd_base = base_data['rd_expense'] if pd.notna(base_data['rd_expense']) else 0
                rd_growth = revenue_growth * 0.8  # R&D grows slower than revenue
                projected_data.loc[year, 'rd_expense'] = rd_base * (1 + rd_growth)
                
                # SG&A with operational leverage
                sga_base = base_data['sga_expense'] if pd.notna(base_data['sga_expense']) else 0
                sga_growth = revenue_growth * 0.6  # SG&A grows much slower than revenue
                projected_data.loc[year, 'sga_expense'] = sga_base * (1 + sga_growth)
            
            # Calculate derived metrics with profitability path for unprofitable companies
            self._calculate_projected_derived_metrics(projected_data, year, base_data, params, scenario, i, 
                                                    target_margin, years_to_profit, is_profitable)
        
        return projected_data
    
    def _calculate_projected_derived_metrics(self, projected_data: pd.DataFrame, year: int, 
                                           base_data: pd.Series, params: ProjectionParams, 
                                           scenario: str, year_index: int,
                                           target_margin: Optional[float], years_to_profit: int, is_profitable: bool):
        """Calculate derived metrics for projected year"""
        
        revenue = projected_data.loc[year, 'revenue']
        cogs = projected_data.loc[year, 'cogs']
        rd_expense = projected_data.loc[year, 'rd_expense']
        sga_expense = projected_data.loc[year, 'sga_expense']
        
        # Gross profit
        if pd.notna(revenue) and pd.notna(cogs):
            projected_data.loc[year, 'gross_profit'] = revenue - cogs
            projected_data.loc[year, 'gross_margin'] = (revenue - cogs) / revenue
        
        # Operating income
        gross_profit = projected_data.loc[year, 'gross_profit']
        if pd.notna(gross_profit):
            total_opex = 0
            if pd.notna(rd_expense):
                total_opex += rd_expense
            if pd.notna(sga_expense):
                total_opex += sga_expense
            
            projected_data.loc[year, 'operating_income'] = gross_profit - total_opex
            if pd.notna(revenue) and revenue > 0:
                projected_data.loc[year, 'operating_margin'] = (gross_profit - total_opex) / revenue
        
        # Net income with improved profitability path
        operating_income = projected_data.loc[year, 'operating_income']
        if pd.notna(operating_income):
            # Apply tax rate (assume 25% effective tax rate)
            tax_rate = 0.25
            if operating_income > 0:
                net_income = operating_income * (1 - tax_rate)
            else:
                net_income = operating_income  # No tax benefit on losses
            
            projected_data.loc[year, 'net_income'] = net_income
            if pd.notna(revenue) and revenue > 0:
                projected_data.loc[year, 'net_margin'] = net_income / revenue
        
        # Cash flow projections
        net_income = projected_data.loc[year, 'net_income']
        if pd.notna(net_income):
            # CFO approximation (Net Income + Depreciation - Working Capital Change)
            depreciation = revenue * 0.02 if pd.notna(revenue) else 0  # Assume 2% of revenue
            working_capital_change = revenue * 0.01 if pd.notna(revenue) else 0  # Assume 1% of revenue
            
            projected_data.loc[year, 'cfo'] = net_income + depreciation - working_capital_change
            
            # CapEx projection
            capex_rate = params.capex_as_pct_revenue.get(scenario, 0.03) if params.capex_as_pct_revenue else 0.03
            capex = revenue * capex_rate if pd.notna(revenue) else 0
            projected_data.loc[year, 'capex'] = -capex  # Negative for cash outflow
            
            # FCF
            cfo = projected_data.loc[year, 'cfo']
            if pd.notna(cfo):
                projected_data.loc[year, 'fcf'] = cfo + capex  # capex is already negative
                if pd.notna(revenue) and revenue > 0:
                    projected_data.loc[year, 'fcf_margin'] = (cfo + capex) / revenue
        
        # Shares and EPS
        shares = base_data['shares_diluted'] if pd.notna(base_data['shares_diluted']) else 800_000_000
        # Assume slight dilution or buybacks
        dilution_rate = params.share_buyback_pct or 0.01  # 1% annual dilution
        projected_shares = shares * (1 + dilution_rate)
        projected_data.loc[year, 'shares_diluted'] = projected_shares
        
        net_income = projected_data.loc[year, 'net_income']
        if pd.notna(net_income) and projected_shares > 0:
            projected_data.loc[year, 'eps'] = net_income / projected_shares
    
    def _load_from_file(self, ticker: str, year: int, input_dir: str) -> Dict[str, Any]:
        """Load XBRL data from file"""
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
                logger.info(f"Loading from file: {file_path}")
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        
        # If no standard format found, look for any JSON file containing ticker and year
        for json_file in input_path.glob("*.json"):
            if ticker.upper() in json_file.name.upper() and str(year) in json_file.name:
                logger.info(f"Loading from file: {json_file}")
                with open(json_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        
        raise FileNotFoundError(f"No XBRL JSON file found for {ticker} {year} in {input_path}")
    
    def _fetch_from_api(self, ticker: str, year: int) -> Dict[str, Any]:
        """Fetch XBRL data from SEC API"""
        from sec_api import QueryApi, XbrlApi
        
        query_api = QueryApi(self.api_key)
        xbrl_api = XbrlApi(self.api_key)
        
        # Get filing URL
        q = {"query": f'ticker:{ticker} AND formType:"10-K" AND filedAt:[{year}-01-01 TO {year}-12-31]',
             "from":0,"size":1,"sort":[{"filedAt":{"order":"desc"}}]}
        filings = query_api.get_filings(q)["filings"]
        if not filings:
            raise ValueError(f"No 10-K for {ticker} {year}")
        
        filing_url = filings[0]["linkToFilingDetails"]
        
        # Get XBRL data
        return xbrl_api.xbrl_to_json(htm_url=filing_url)
    
    def calculate_valuation_metrics(self, projections: Dict[str, pd.DataFrame], 
                                  params: ProjectionParams) -> Dict[str, Dict[str, float]]:
        """Calculate valuation metrics for all scenarios"""
        
        valuations = {}
        
        for scenario, df in projections.items():
            if scenario == 'historical':
                continue
            
            # Calculate DCF valuation
            fcf_values = df['fcf'].dropna().values
            if len(fcf_values) > 0:
                dcf_value = self._calculate_dcf_value(fcf_values, params)
                
                # Calculate other valuation metrics
                last_year_metrics = df.iloc[-1]
                pe_multiple = 15  # Assume P/E multiple based on scenario
                if scenario == 'bear':
                    pe_multiple = 12
                elif scenario == 'bull':
                    pe_multiple = 20
                
                pe_value = last_year_metrics.get('net_income', 0) * pe_multiple
                
                valuations[scenario] = {
                    'dcf_value': dcf_value,
                    'pe_value': pe_value,
                    'final_year_fcf': fcf_values[-1] if len(fcf_values) > 0 else 0,
                    'final_year_eps': last_year_metrics.get('eps', 0)
                }
        
        return valuations
    
    def _calculate_dcf_value(self, fcf_values: List[float], params: ProjectionParams) -> float:
        """Calculate DCF value from FCF projections"""
        
        # Calculate present value of projected FCFs
        pv_fcf = 0
        for i, fcf in enumerate(fcf_values):
            if pd.notna(fcf):
                pv_fcf += fcf / ((1 + params.discount_rate) ** (i + 1))
        
        # Calculate terminal value
        if len(fcf_values) > 0:
            terminal_fcf = fcf_values[-1] * (1 + params.terminal_growth_rate)
            terminal_value = terminal_fcf / (params.discount_rate - params.terminal_growth_rate)
            pv_terminal = terminal_value / ((1 + params.discount_rate) ** len(fcf_values))
        else:
            pv_terminal = 0
        
        return pv_fcf + pv_terminal
    
    def run_comprehensive_analysis(self, ticker: str, params: ProjectionParams, 
                                 from_files: bool = False, input_dir: str = "./input",
                                 output_dir: str = "./output") -> Dict[str, Any]:
        """Run comprehensive financial analysis"""
        
        logger.info(f"Starting comprehensive analysis for {ticker}")
        
        # Build projections
        projections = self.build_projections(ticker, params, from_files, input_dir)
        
        # Calculate valuations
        valuations = self.calculate_valuation_metrics(projections, params)
        
        # Generate summary statistics
        summary_stats = self._generate_summary_statistics(projections, valuations)
        
        # Save results
        self._save_results(ticker, projections, valuations, summary_stats, output_dir)
        
        return {
            'projections': projections,
            'valuations': valuations,
            'summary_stats': summary_stats
        }
    
    def _generate_summary_statistics(self, projections: Dict[str, pd.DataFrame], 
                                   valuations: Dict[str, Dict[str, float]]) -> Dict[str, Any]:
        """Generate summary statistics"""
        
        stats = {}
        
        # Revenue CAGR for each scenario
        for scenario in ['bear', 'base', 'bull']:
            if scenario in projections:
                df = projections[scenario]
                first_revenue = df['revenue'].iloc[0]
                last_revenue = df['revenue'].iloc[-1]
                
                if pd.notna(first_revenue) and pd.notna(last_revenue) and first_revenue > 0:
                    years = len(df) - 1
                    cagr = (last_revenue / first_revenue) ** (1/years) - 1
                    stats[f'{scenario}_revenue_cagr'] = cagr
        
        # Profitability metrics
        historical = projections.get('historical')
        if historical is not None:
            stats['historical_avg_net_margin'] = historical['net_margin'].mean()
            stats['historical_avg_fcf_margin'] = historical['fcf_margin'].mean()
        
        return stats
    
    def _save_results(self, ticker: str, projections: Dict[str, pd.DataFrame], 
                     valuations: Dict[str, Dict[str, float]], summary_stats: Dict[str, Any],
                     output_dir: str):
        """Save analysis results"""
        
        output_path = Path(output_dir) / f"{ticker}_analysis"
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save projections
        for scenario, df in projections.items():
            df.to_csv(output_path / f"{ticker}_{scenario}.csv")
        
        # Save valuations
        with open(output_path / f"{ticker}_valuations.json", 'w') as f:
            json.dump(valuations, f, indent=2)
        
        # Save summary
        with open(output_path / f"{ticker}_summary.json", 'w') as f:
            json.dump(summary_stats, f, indent=2)
        
        logger.info(f"Results saved to {output_path}") 