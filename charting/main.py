import os
import pandas as pd
import dash
from dash import html, dcc, dash_table
import plotly.graph_objs as go
import argparse
import plotly.io as pio
from pathlib import Path
import re


CURRENT_DIR = Path(__file__).parent

# ---- COMMAND LINE ARGUMENTS ----
parser = argparse.ArgumentParser(description='Financial Model Dashboard with PNG Export')
parser.add_argument('--ticker', type=str, default='AAPL', help='Stock ticker symbol (default: AAPL)')
parser.add_argument('--input-dir', type=str, default=str(CURRENT_DIR / "../projections/output"), help='Directory containing CSV files (default: ./output)')
parser.add_argument('--pe-bear', type=float, default=25, help='P/E ratio for Bear case (default: 25)')
parser.add_argument('--pe-base', type=float, default=30, help='P/E ratio for Base case (default: 30)')
parser.add_argument('--pe-bull', type=float, default=35, help='P/E ratio for Bull case (default: 35)')
parser.add_argument('--current-year', type=str, default='2025', help='Current year (default: 2025)')
parser.add_argument('--current-price', type=float, default=201, help='Current stock price (default: 201)')
parser.add_argument('--download', action='store_true', help='Download revenue tables as PNG files', default=True)
parser.add_argument('--port', type=int, default=8050, help='Port for Dash app (default: 8050)')
parser.add_argument('--charts', action='store_true', help='Show charts',default=False)
args = parser.parse_args()

# ---- CONFIGURATION ----
DATA_DIR = args.input_dir
PE_MAP = {
    "Bear": args.pe_bear,
    "Base": args.pe_base,
    "Bull": args.pe_bull
}
CURRENT_YEAR = args.current_year
CURRENT_YEAR_PRICE = args.current_price

# Create TICKER_TABLES directory for PNG exports
TICKER_TABLES_DIR = CURRENT_DIR / "output"
if args.download:
    TICKER_TABLES_DIR.mkdir(parents=True, exist_ok=True)

def camel_to_spaces(s):
    """
    Convert a camel case string to a space separated string.
    """
    return re.sub(r'(?<=[a-z0-9])(?=[A-Z])', ' ', s)

def format_large_number(val, metric):
    """Format large numbers in millions format if they exceed 100,000,000"""
    if pd.isna(val):
        return ""
    
    try:
        val_float = float(val)
        if val_float > 100_000_000 and metric in ["Revenue", "NetIncome", "FCF"]:
            return f"${val_float / 1_000_000:.1f}M"
        elif metric == "Price":
            return f"${val_float:.2f}"
        elif metric in ["Revenue", "NetIncome", "FCF"]:
            return f"${val_float:,.0f}"
        elif metric in ["GrossMargin", "OperatingMargin", "NetMargin", "FCFMargin"]:
            return f"{val_float:.1f}%"
        elif metric == "EPS":
            return f"${val_float:.2f}"
        else:
            return f"{val_float:.2f}"
    except Exception:
        return str(val)

def load_csv(name):
    """
    Load a CSV file from the data directory.
    """
    for fname in os.listdir(DATA_DIR):
        if fname.lower().startswith(name.lower()) and fname.lower().endswith('.csv'):
            file_path = os.path.join(DATA_DIR, fname)
            return pd.read_csv(file_path, index_col=0)
    
    return None

dfs = {
    "Historical": load_csv(f"{args.ticker}_historical"),
    "Bear": load_csv(f"{args.ticker}_bear"),
    "Base": load_csv(f"{args.ticker}_base"),
    "Bull": load_csv(f"{args.ticker}_bull"),
}

# Check if any dataframes are None and handle gracefully
if any(df is None for df in dfs.values()):
    print("Error: Some CSV files could not be loaded. Available files:")
    if os.path.exists(DATA_DIR):
        for fname in os.listdir(DATA_DIR):
            if fname.lower().endswith('.csv'):
                print(f"  - {fname}")
    else:
        print(f"Directory {DATA_DIR} does not exist")
    print("Exiting...")
    exit(1)

years = dfs["Historical"].columns.tolist()
main_metrics = [
    "Revenue", "NetIncome", "EPS", "GrossMargin", "OperatingMargin",
    "NetMargin", "FCF", "FCFMargin"
]

def create_revenue_table_figure(scenario):
    """Create a figure specifically for revenue table export"""
    df = dfs[scenario].copy()
    # remove the last 4 years
    df = df.iloc[:, 4:]

    # Add projected price
    pe = PE_MAP.get(scenario, 25)
    projected_price = []
    if "EPS" in df.index:
        eps = df.loc["EPS"]
        for y in df.columns:
            if y == CURRENT_YEAR:
                projected_price.append(CURRENT_YEAR_PRICE)
            elif not pd.isna(eps[y]):
                try:
                    projected_price.append(round(float(eps[y]) * pe, 2))
                except Exception:
                    projected_price.append("")
            else:
                projected_price.append("")
        df.loc["Price"] = projected_price

    # Create table data with all metrics
    table_data = []
    headers = ['Metric'] + list(df.columns)
    
    # Add all main metrics + ProjectedPrice
    for metric in main_metrics + ["Price"]:
        if metric in df.index:
            metric_name = camel_to_spaces(metric)
            if metric == "FCFMargin":
                metric_name = "FCF Margin"
            row = [metric_name]
            for col in df.columns:
                val = df.loc[metric, col]
                if pd.isna(val):
                    row.append("")
                else:
                    if metric == "Price":
                        row.append(format_large_number(val, metric))
                    elif metric in ["Revenue", "NetIncome", "FCF"]:
                        row.append(format_large_number(val, metric))
                    elif metric in ["GrossMargin", "OperatingMargin", "NetMargin", "FCFMargin"]:
                        row.append(format_large_number(val, metric))
                    elif metric == "EPS":
                        row.append(format_large_number(val, metric))
                    else:
                        row.append(format_large_number(val, metric))
            table_data.append(row)

    fig = go.Figure(data=[go.Table(
        columnwidth=[180] + [80] * (len(df.columns)),  # 180px for first column, 80px for the rest
        header=dict(
            values=headers,
            fill_color='#e9ecef',
            font=dict(size=14, color='black', family='Arial, sans-serif'),
            align='center',
            height=35,
            line=dict(color='#ced4da', width=2)
        ),
        cells=dict(
            values=list(zip(*table_data)),
            fill_color=[['#f0f2f4', '#ffffff'] * (len(table_data)//2 + 1)][:len(table_data)],
            font=dict(size=12, color='black', family='Arial, sans-serif'),
            height=30,
            align='center',
            line=dict(color='#dee2e6', width=1)
        )
    )])

    fig.update_layout(
        title=f"{args.ticker} - {scenario} Case Financial Projections",
        title_font=dict(size=16, family='Arial, sans-serif'),
        width=1000,
        height=400,
        margin=dict(l=20, r=20, t=60, b=20)
    )
    return fig

def export_revenue_tables_png():
    """Export revenue tables as PNG files"""


    scenarios = ["Bear", "Base", "Bull"]
    for scenario in scenarios:
        fig = create_revenue_table_figure(scenario)
        filename = TICKER_TABLES_DIR / f"{args.ticker}_{scenario.lower()}_revenue_table.png"
        pio.write_image(fig, str(filename), format='png')
        print(f"Exported {filename}")

def scenario_charts_table(scenario):
    """
    Create a table for a given scenario.
    """
    df = dfs[scenario].copy()
    cards = []

    # --- Add Projected Price ---
    pe = PE_MAP.get(scenario, 25)
    projected_price = []
    if "EPS" in df.index:
        eps = df.loc["EPS"]
        for y in df.columns:
            if y == CURRENT_YEAR:
                projected_price.append(CURRENT_YEAR_PRICE)
            elif not pd.isna(eps[y]):
                try:
                    projected_price.append(round(float(eps[y]) * pe, 2) / 1_00)
                except Exception:
                    projected_price.append("")
            else:
                projected_price.append("")
        df.loc["Price"] = projected_price

    # --- Plot each metric (main metrics + ProjectedPrice) ---
    for metric in main_metrics + ["Price"]:
        if metric in df.index:
            yvals = df.loc[metric].values
            years = df.columns.tolist()

            # % change (skip for ProjectedPrice)
            pct = [""]
            for i in range(1, len(yvals)):
                try:
                    prev = float(yvals[i-1])
                    now = float(yvals[i])
                    if metric == "Price":
                        pct.append("")
                    elif prev == 0 or pd.isna(prev) or pd.isna(now):
                        pct.append("")
                    else:
                        change = 100 * (now - prev) / abs(prev)
                        pct.append(f"{change:+.1f}%")
                except Exception:
                    pct.append("")
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=years, y=yvals,
                mode='lines+markers+text',
                name=scenario if metric != "Price" else "Projected Price",
                text=pct,
                textposition="top center",
                textfont=dict(size=13, color="black"),
                hovertemplate="%{y}<br>%{text} from last year<extra></extra>",
                marker=dict(size=8)
            ))
            fig.update_layout(
                title=f"{camel_to_spaces(metric)} — {scenario} Case",
                legend=dict(x=0.01, y=0.98),
                margin={"r":0,"t":30,"l":0,"b":0},
                height=300,
                plot_bgcolor="#fafbfc",
                paper_bgcolor="#fafbfc",
                font=dict(family="Inter, Arial, sans-serif", size=15)
            )
            cards.append(dcc.Graph(figure=fig, style={"marginBottom": "32px"}))

    # --- Table for scenario ---
    df_disp = df.loc[[m for m in main_metrics + ["Price"] if m in df.index]]
    df_disp = df_disp.reset_index().rename(columns={'index': 'Metric'})

    # Apply camel_to_spaces to 'Metric' column for display
    df_disp["Metric"] = df_disp["Metric"].apply(camel_to_spaces)

    # Format large numbers in the DataFrame
    for metric in main_metrics + ["Price"]:
        if metric in df.index:
            metric_name = camel_to_spaces(metric)
            if metric == "FCFMargin":
                metric_name = "FCF Margin"
            
            for col in df_disp.columns[1:]:  # Skip the 'Metric' column
                if metric_name in df_disp['Metric'].values:
                    row_idx = df_disp[df_disp['Metric'] == metric_name].index[0]
                    val = df_disp.loc[row_idx, col]
                    if not pd.isna(val):
                        df_disp.loc[row_idx, col] = format_large_number(val, metric)

    cards.append(html.H4(f"{scenario} Table", style={"marginTop": "30px", "marginBottom": "10px"}))
    cards.append(dash_table.DataTable(
        data=df_disp.to_dict("records"),
        columns=[{"name": c, "id": c} for c in df_disp.columns],
        style_table={'overflowX': 'auto', "padding": "0", "marginBottom": "32px"},
        style_data={
            'backgroundColor': '#fff',
            'color': '#222',
            'fontSize': 16,
            'padding': "8px",
        },
        style_header={
            'backgroundColor': '#e9ecef',
            'fontWeight': 'bold',
            'fontSize': 17,
            'borderTop': '2px solid #ced4da',
            'borderBottom': '2px solid #ced4da'
        },
        style_cell={
            'textAlign': 'center',
            'minWidth': '90px', 'width': '90px', 'maxWidth': '120px',
            'padding': "8px"
        },
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': '#f6f8fa'
            },
            {
                'if': {'column_id': 'Metric'},
                'textAlign': 'left',
                'fontWeight': 'bold',
                'backgroundColor': '#f0f2f4'
            }
        ]
    ))
    return html.Div(
        cards,
        style={
            "background": "#fff",
            "borderRadius": "18px",
            "boxShadow": "0 6px 24px 0 rgba(0,0,0,0.06)",
            "padding": "32px 32px 16px 32px",
            "marginBottom": "36px"
        }
    )

app = dash.Dash(__name__)
app.layout = html.Div([
    html.H1(f"{args.ticker} Financial Model Dashboard", style={"marginTop":"28px", "marginBottom":"8px", "fontFamily":"Inter, Arial, sans-serif"}),
    html.H3("Historical, Bear, Base, and Bull Scenarios", style={"color":"#444", "fontFamily":"Inter, Arial, sans-serif", "marginBottom":"22px"}),
    html.Div([
        html.H2("Bear Case", style={"marginTop":"12px", "color":"#ce3c3c", "fontFamily":"Inter, Arial, sans-serif"}),
        scenario_charts_table("Bear"),
        html.H2("Base Case", style={"marginTop":"12px", "color":"#368fc7", "fontFamily":"Inter, Arial, sans-serif"}),
        scenario_charts_table("Base"),
        html.H2("Bull Case", style={"marginTop":"12px", "color":"#18a551", "fontFamily":"Inter, Arial, sans-serif"}),
        scenario_charts_table("Bull"),
        html.H2("Historical Data", style={"marginTop":"12px", "color":"#444", "fontFamily":"Inter, Arial, sans-serif"}),
        scenario_charts_table("Historical"),
    ], style={"overflowY": "auto", "height": "90vh", "padding": "30px"})
], style={
    "background": "#f3f4f7",
    "minHeight": "100vh",
    "fontFamily":"Inter, Arial, sans-serif"
})

if __name__ == "__main__":
    # Export PNG files if requested
    if args.download:
        print("Exporting PNG files")
        export_revenue_tables_png()
    if args.charts:
        print("Starting Dash app")
        app.run(debug=True, port=args.port)
