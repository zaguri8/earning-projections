import pandas as pd
from typing import List, Optional

class PriceProjector:
    def __init__(self, pe_ratio: float, current_year: str, current_price: float, 
                 target_pe: Optional[float] = None, years_to_profitability: int = 3):
        self.pe_ratio = pe_ratio
        self.current_year = current_year
        self.current_price = current_price
        self.target_pe = target_pe if target_pe is not None else pe_ratio
        self.years_to_profitability = years_to_profitability

    def project_prices(self, df: pd.DataFrame) -> List[Optional[float]]:
        """
        Compute projected prices for each year in the DataFrame.
        If EPS is negative, project toward a target PE over years_to_profitability.
        """
        if "EPS" not in df.index:
            return [None for _ in df.columns]
        eps = df.loc["EPS"]
        years = df.columns
        projected_price = []
        last_positive_pe = self.pe_ratio
        for i, y in enumerate(years):
            if y == self.current_year:
                projected_price.append(self.current_price)
                continue
            try:
                eps_val = float(eps[y])
            except Exception:
                projected_price.append("")
                continue
            if pd.isna(eps_val):
                projected_price.append("")
                continue
            # If EPS is positive, use normal PE
            if eps_val > 0:
                price = round(eps_val * self.pe_ratio, 2)
                projected_price.append(price)
                last_positive_pe = self.pe_ratio
            else:
                # If EPS is negative, project toward target PE (or price) over N years
                # Use linear improvement: price = current + (target - current) * (step / N)
                # Target price is abs(target_pe * |eps|) (or 0 if you want to show no value)
                # We'll project toward breakeven (price=0) or a small positive price
                # For realism, let's project toward a small positive price (e.g., target_pe * 0.01)
                idx_from_current = i - list(years).index(self.current_year)
                if idx_from_current <= 0:
                    projected_price.append("")
                    continue
                # Target: small positive price (e.g., $1.00 or target_pe * 0.01)
                target_price = round(self.target_pe * 0.01, 2)
                # Start from previous price (or current_price if first year)
                prev_price = projected_price[-1] if projected_price[-1] not in (None, "") else self.current_price
                # Linear improvement
                step = min(idx_from_current, self.years_to_profitability)
                total_steps = self.years_to_profitability
                price = prev_price + (target_price - prev_price) * (step / total_steps)
                projected_price.append(round(price, 2))
        return projected_price 