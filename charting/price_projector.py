import pandas as pd
from typing import List, Optional, Dict

class PriceProjector:
    """Enhanced price projection with better error handling and flexibility"""
    
    def __init__(self, pe_ratio: float, current_year: str, current_price: float, 
                 target_pe: Optional[float] = None, years_to_profitability: int = 3):
        self.pe_ratio = pe_ratio
        self.current_year = str(current_year)
        self.current_price = current_price
        self.target_pe = target_pe if target_pe is not None else pe_ratio
        self.years_to_profitability = years_to_profitability
    
    def find_eps_key(self, df: pd.DataFrame) -> Optional[str]:
        """Find EPS key in DataFrame (case insensitive)"""
        for key in df.index:
            if key.lower() == "eps":
                return key
        return None
    
    def project_prices(self, df: pd.DataFrame) -> List[Optional[float]]:
        """Project stock prices based on EPS and PE ratios"""
        eps_key = self.find_eps_key(df)
        
        if eps_key is None:
            print(f"Warning: EPS not found in DataFrame index: {df.index.tolist()}")
            return [None for _ in df.columns]
        
        eps = df.loc[eps_key]
        
        # Use original column values (integers) instead of converting to strings
        years = df.columns.tolist()
        projected_prices = []
        
        # Find current year index
        current_year_idx = None
        for i, year in enumerate(years):
            if str(year) == self.current_year:
                current_year_idx = i
                break
        
        if current_year_idx is None:
            print(f"Warning: Current year {self.current_year} not found. Using first year.")
            current_year_idx = 0
        
        for i, year in enumerate(years):
            if str(year) == self.current_year:
                projected_prices.append(self.current_price)
                continue
            
            try:
                eps_val = float(eps[year])
            except (ValueError, TypeError, KeyError) as e:
                print(f"Warning: Error accessing EPS for year {year}: {e}")
                projected_prices.append(None)
                continue
            
            if pd.isna(eps_val):
                projected_prices.append(None)
                continue
            
            if eps_val > 0:
                # Positive EPS: use PE ratio
                price = round(eps_val * self.pe_ratio, 2)
                projected_prices.append(price)
            else:
                # Negative EPS: project toward profitability
                years_from_current = i - current_year_idx
                if years_from_current <= 0:
                    projected_prices.append(None)
                    continue
                
                # Linear progression toward target price
                target_price = self.target_pe * 0.01  # Small positive target
                prev_price = projected_prices[-1] if projected_prices and projected_prices[-1] is not None else self.current_price
                
                progress = min(years_from_current / self.years_to_profitability, 1.0)
                price = prev_price + (target_price - prev_price) * progress
                projected_prices.append(round(price, 2))
        
        return projected_prices
