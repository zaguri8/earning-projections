import pandas as pd
import os
from typing import Dict, Optional
from config import DashboardConfig

class DataManager:
    """Handles loading and processing of financial data"""
    
    def __init__(self, config: DashboardConfig):
        self.config = config
        self._data_cache: Dict[str, pd.DataFrame] = {}
    
    def load_csv(self, scenario_name: str) -> Optional[pd.DataFrame]:
        """Load CSV file for a given scenario"""
        if scenario_name in self._data_cache:
            return self._data_cache[scenario_name]
        
        # Try different filename patterns
        patterns = [
            f"{self.config.ticker}_{scenario_name.lower()}",
            f"{scenario_name.lower()}_{self.config.ticker}",
            f"{self.config.ticker}_{scenario_name}",
        ]
        
        for pattern in patterns:
            for fname in os.listdir(self.config.data_dir):
                if fname.lower().startswith(pattern.lower()) and fname.lower().endswith('.csv'):
                    file_path = self.config.data_dir / fname
                    try:
                        df = pd.read_csv(file_path, index_col=0)
                        self._data_cache[scenario_name] = df
                        return df
                    except Exception as e:
                        print(f"Error loading {file_path}: {e}")
        
        print(f"Warning: Could not find CSV file for {scenario_name}")
        return None
    
    def load_all_data(self) -> Dict[str, pd.DataFrame]:
        """Load all scenario data"""
        data = {}
        for scenario in self.config.scenarios:
            df = self.load_csv(scenario.name)
            if df is not None:
                data[scenario.name] = df
        return data
    
    def validate_data(self, data: Dict[str, pd.DataFrame]) -> bool:
        """Validate that required data is present"""
        if not data:
            print("Error: No data loaded")
            return False
        
        required_metrics = [m.name for m in self.config.metrics]
        for scenario_name, df in data.items():
            missing_metrics = [m for m in required_metrics if m not in df.index]
            if missing_metrics:
                print(f"Warning: Missing metrics in {scenario_name}: {missing_metrics}")
        
        return True