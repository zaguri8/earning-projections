#!/usr/bin/env python3
"""
Test script to demonstrate the profitability fix for unprofitable companies.
"""

import pandas as pd
import sys
import os
sys.path.append(os.path.dirname(__file__))

from main import _proj, build_projections

def test_profitability_fix():
    """Test the difference between old and new projection logic"""
    
    # Create sample data for an unprofitable company (similar to GTLB)
    sample_data = pd.DataFrame({
        '2022': {
            'Revenue': 81227000.0,
            'OperatingIncome': -128367000.0,
            'NetIncome': -130741000.0,
            'CFO': -60166000.0,
            'GrossProfit': 71851000.0
        },
        '2023': {
            'Revenue': 152176000.0,
            'OperatingIncome': -213884000.0,
            'NetIncome': -192194000.0,
            'CFO': -73580000.0,
            'GrossProfit': 133713000.0
        },
        '2024': {
            'Revenue': 252653000.0,
            'OperatingIncome': -128957000.0,
            'NetIncome': -155138000.0,
            'CFO': -49814000.0,
            'GrossProfit': 222668000.0
        }
    })
    
    growth_assumptions = {
        "revenue": {"bear": 0.02, "base": 0.05, "bull": 0.09}
    }
    
    print("=== UNPROFITABLE COMPANY PROJECTION TEST ===\n")
    
    # Test with new logic (targeting profitability)
    print("NEW LOGIC (Targeting 10% profit margin over 3 years):")
    new_proj = _proj(sample_data, 2025, 5, growth_assumptions, "base", 
                     profit_margin_target=0.10, years_to_profitability=3)
    
    print("Operating Income progression:")
    for year in ['2024', '2025', '2026', '2027', '2028', '2029']:
        if year in new_proj.columns:
            value = new_proj.loc['OperatingIncome', year]
            print(f"  {year}: ${value:,.0f}")
    
    print("\nNet Income progression:")
    for year in ['2024', '2025', '2026', '2027', '2028', '2029']:
        if year in new_proj.columns:
            value = new_proj.loc['NetIncome', year]
            print(f"  {year}: ${value:,.0f}")
    
    print("\nOperating Margin progression:")
    for year in ['2024', '2025', '2026', '2027', '2028', '2029']:
        if year in new_proj.columns:
            if 'OperatingMargin' in new_proj.index:
                value = new_proj.loc['OperatingMargin', year]
                print(f"  {year}: {value:.1%}")
            else:
                # Calculate manually
                revenue = new_proj.loc['Revenue', year]
                op_income = new_proj.loc['OperatingIncome', year]
                if revenue and revenue > 0:
                    margin = op_income / revenue
                    print(f"  {year}: {margin:.1%}")
                else:
                    print(f"  {year}: N/A")
    
    print("\n" + "="*50)
    
    # Test with old logic (simple growth rate application)
    print("OLD LOGIC (Simple growth rate application):")
    old_proj = _proj(sample_data, 2025, 5, growth_assumptions, "base", 
                     profit_margin_target=None, years_to_profitability=5)
    
    print("Operating Income progression (OLD):")
    for year in ['2024', '2025', '2026', '2027', '2028', '2029']:
        if year in old_proj.columns:
            value = old_proj.loc['OperatingIncome', year]
            print(f"  {year}: ${value:,.0f}")
    
    print("\nNet Income progression (OLD):")
    for year in ['2024', '2025', '2026', '2027', '2028', '2029']:
        if year in old_proj.columns:
            value = old_proj.loc['NetIncome', year]
            print(f"  {year}: ${value:,.0f}")
    
    print("\nOperating Margin progression (OLD):")
    for year in ['2024', '2025', '2026', '2027', '2028', '2029']:
        if year in old_proj.columns:
            if 'OperatingMargin' in old_proj.index:
                value = old_proj.loc['OperatingMargin', year]
                print(f"  {year}: {value:.1%}")
            else:
                # Calculate manually
                revenue = old_proj.loc['Revenue', year]
                op_income = old_proj.loc['OperatingIncome', year]
                if revenue and revenue > 0:
                    margin = op_income / revenue
                    print(f"  {year}: {margin:.1%}")
                else:
                    print(f"  {year}: N/A")
    
    print("\n" + "="*50)
    print("SUMMARY:")
    print("OLD LOGIC: Applied growth rates directly to negative values,")
    print("           making losses worse over time (mathematically correct but")
    print("           financially unrealistic for projections)")
    print("\nNEW LOGIC: Projects toward profitability with target margins,")
    print("           showing realistic path to breakeven and profitability")

if __name__ == "__main__":
    test_profitability_fix() 