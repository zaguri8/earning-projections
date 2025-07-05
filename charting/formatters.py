import pandas as pd
import re

class DataFormatter:
    """Handles formatting of financial data for display"""
    
    @staticmethod
    def camel_to_spaces(s: str) -> str:
        """Convert camelCase to spaced string"""
        return re.sub(r'(?<=[a-z0-9])(?=[A-Z])', ' ', s)
    
    @staticmethod
    def format_value(value, format_type: str) -> str:
        """Format a value based on its type"""
        if pd.isna(value):
            return ""
        
        try:
            val_float = float(value)
            
            if format_type == "currency":
                if val_float > 100_000_000:
                    return f"${val_float / 1_000_000:.1f}M"
                elif val_float > 1_000_000:
                    return f"${val_float / 1_000_000:.2f}M"
                else:
                    return f"${val_float:,.0f}"
            
            elif format_type == "percentage":
                return f"{val_float:.1f}%"
            
            elif format_type == "price":
                return f"${val_float:.2f}"
            
            elif format_type == "number":
                if val_float > 1_000_000:
                    return f"{val_float / 1_000_000:.1f}M"
                else:
                    return f"{val_float:,.0f}"
            
            else:
                return f"{val_float:.2f}"
                
        except Exception:
            return str(value)
    
    @staticmethod
    def calculate_growth(current_val, previous_val) -> str:
        """Calculate and format growth percentage"""
        try:
            current = float(current_val)
            previous = float(previous_val)
            
            if previous == 0 or pd.isna(previous) or pd.isna(current):
                return ""
            
            growth = (current - previous) / abs(previous) * 100
            return f"{growth:+.1f}%"
        
        except (ValueError, TypeError):
            return ""
