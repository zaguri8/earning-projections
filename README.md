# 🚀 SEC 10-K Financial Analysis Suite

> **The ULTIMATE financial modeling toolkit** that transforms SEC filings into 🔥 **LIT AF** projections and visualizations!

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)]()

---

## 🎯 What This Bad Boy Does

This suite is your **one-stop-shop** for financial analysis that'll make your portfolio go 📈 **TO THE MOON**! 

### ✨ Features That'll Blow Your Mind

- 🔥 **Automated SEC Filing Downloads** - No more manual digging through EDGAR
- 📊 **Smart Financial Projections** - Bear, Base, and Bull scenarios (because we're not psychic)
- 📈 **Beautiful Interactive Dashboards** - Charts so pretty they belong in a museum
- 🎨 **Professional PNG Exports** - Ready for your next investor pitch
- ⚡ **Modular Architecture** - Each component is a beast on its own

---

## 🏗️ Architecture Overview

```
earning-projections/
├── 📁 filings/          # SEC filing downloader
├── 📁 projections/      # Financial modeling engine  
├── 📁 charting/         # Visualization & dashboard
├── 📁 utils/           # Shared utilities
└── 🚀 main.py          # Master orchestrator
```

---

## 🚀 Quick Start (The LIT Way)

### 1. Setup Your Environment

```bash
# Clone this beast
git clone <your-repo>
cd earning-projections

# Create your virtual environment (because we're professionals)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the dependencies (this is where the magic happens)
pip install -r requirements.txt
```

### 2. Set Your SEC API Key

```bash
# Get your free API key from https://sec-api.io
export SEC_API_KEY="your_api_key_here"
```

### 3. Run the Full Pipeline (The Easy Way)

```bash
# This runs EVERYTHING for AAPL (default)
python main.py --ticker AAPL

# Or customize your growth assumptions
python main.py --ticker GOOGL \
  --growth-bear 0.03 \
  --growth-base 0.08 \
  --growth-bull 0.15 \
  --pe-bear 20 \
  --pe-base 25 \
  --pe-bull 30
```

---

## 🎮 Individual Package Usage

### 📁 Filings Package - Data Collection Beast

```bash
# Download 5 years of SEC filings
python filings/main.py --ticker AAPL --start-year 2020 --end-year 2024

# Customize your data range
python filings/main.py --ticker TSLA --start-year 2019 --end-year 2023
```

**Output**: JSON files with structured financial data in `filings/output/`

### 📊 Projections Package - Financial Modeling Wizard

```bash
# Generate projections with default assumptions
python projections/main.py --ticker AAPL

# Custom growth rates for different scenarios
python projections/main.py --ticker NVDA \
  --growth-bear 0.05 \
  --growth-base 0.12 \
  --growth-bull 0.25
```

**Output**: CSV files with historical data and projections in `projections/output/`

### 📈 Charting Package - Visualization Masterpiece

```bash
# Create interactive dashboard + PNG exports
python charting/main.py --ticker AAPL --charts

# Custom P/E ratios and current price
python charting/main.py --ticker MSFT \
  --pe-bear 20 \
  --pe-base 30 \
  --pe-bull 40 \
  --current-price 350
```

**Output**: 
- Interactive Dash dashboard (http://localhost:8050)
- Professional PNG tables in `charting/output/`

---

## 🎯 What You Get (The Good Stuff)

### 📊 Financial Metrics Extracted

- **Revenue** - The money maker 💰
- **Net Income** - Pure profit 🎯
- **EPS** - Earnings per share 📈
- **Gross Margin** - Efficiency indicator ⚡
- **Operating Margin** - Operational excellence 🏆
- **Net Margin** - Bottom line performance 📊
- **FCF** - Free cash flow (the real MVP) 💎
- **FCF Margin** - Cash generation efficiency 🔥

### 📈 Projection Scenarios

1. **🐻 Bear Case** - Conservative growth (2-5%)
2. **📊 Base Case** - Realistic growth (5-12%) 
3. **🚀 Bull Case** - Aggressive growth (9-25%)

### 🎨 Visual Outputs

- **Interactive Dashboards** - Real-time data exploration
- **Professional Tables** - PNG exports ready for presentations
- **Growth Charts** - Visual trend analysis
- **Valuation Models** - P/E based price projections

---

## ⚙️ Configuration Options

### Growth Assumptions (JSON Format)

```json
{
  "revenue": {
    "bear": 0.02,   // 2% growth
    "base": 0.08,   // 8% growth  
    "bull": 0.15    // 15% growth
  }
}
```

### P/E Ratios by Scenario

```bash
--pe-bear 20    # Conservative valuation
--pe-base 30    # Fair value
--pe-bull 40    # Growth premium
```

---

## 🔧 Advanced Usage

### Python API (For the Coders)

```python
from projections.main import build_projections

# Build custom projections
hist, (bear, base, bull) = build_projections(
    ticker="AAPL",
    years_back=5,
    current_year=2025,
    proj_years=5,
    growth={
        "revenue": {"bear": 0.03, "base": 0.08, "bull": 0.15}
    }
)
```

### Batch Processing

```bash
# Process multiple tickers
for ticker in AAPL GOOGL MSFT NVDA; do
  python main.py --ticker $ticker
done
```

---

## 📁 Output Structure

```
output/
├── 📊 filings/
│   ├── AAPL_2020.json
│   ├── AAPL_2021.json
│   └── ...
├── 📈 projections/
│   ├── AAPL_historical.csv
│   ├── AAPL_bear.csv
│   ├── AAPL_base.csv
│   └── AAPL_bull.csv
└── 🎨 charting/
    ├── AAPL_bear_revenue_table.png
    ├── AAPL_base_revenue_table.png
    └── AAPL_bull_revenue_table.png
```

---

## 🛠️ Dependencies

- **Python 3.7+** - Because we're not savages
- **pandas** - Data manipulation wizardry
- **dash** - Interactive dashboard magic
- **plotly** - Beautiful visualizations
- **sec-api** - SEC data access (requires API key)
- **tqdm** - Progress bars (because waiting sucks)

---

## 🚨 Troubleshooting

### Common Issues

1. **SEC API Key Missing**
   ```bash
   export SEC_API_KEY="your_key_here"
   ```

2. **Missing Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **File Not Found Errors**
   - Ensure you run filings before projections
   - Check that output directories exist

### Debug Mode

```bash
# Enable debug output
export DEBUG=1
python main.py --ticker AAPL
```

---

## 🤝 Contributing

Want to make this even more LIT? 

1. Fork this beast
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **SEC EDGAR** - For the raw financial data
- **SEC-API** - For making data access easy
- **Plotly** - For the beautiful visualizations
- **Dash** - For the interactive dashboards

---

## 📞 Support

Having issues? This tool is so LIT it might be too hot to handle! 

- Create an issue on GitHub
- Check the troubleshooting section above
- Make sure your SEC API key is valid

---

**Remember**: This tool is for educational and research purposes. Always do your own due diligence before making investment decisions! 📚💡

---

<div align="center">

**Made with ❤️ and ☕ by financial modeling enthusiasts**

*"In a world full of spreadsheets, be a dashboard"* 📊✨

</div> 