# Financial Projections Frontend

A modern Angular application for generating and visualizing financial projections for stocks.

## Features

- **Interactive Form**: Input ticker symbols and projection parameters
- **Real-time API Integration**: Connects to Python backend for projections
- **Chart Display**: Shows revenue, profit, and price projections
- **Download Charts**: Save generated charts as PNG files
- **Responsive Design**: Works on desktop and mobile devices
- **Tailwind CSS**: Modern, utility-first styling

## Setup

### Prerequisites

- Node.js v20+ (managed by nvm)
- Angular CLI
- Python backend running on port 5001

### Installation

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start the development server:
   ```bash
   npm start
   ```

3. Open your browser to `http://localhost:4200`

## Usage

1. **Enter Ticker Symbol**: Input a stock ticker (e.g., AAPL, GTLB)
2. **Configure Parameters**: 
   - For unprofitable companies: Set profit margin target, years to profitability, target P/E
   - For all companies: Set bear/base/bull P/E ratios and growth rates
3. **Generate Projections**: Click the button to run the analysis
4. **View Results**: See revenue, profit, and price projection charts
5. **Download Charts**: Save individual charts as PNG files

## API Integration

The frontend communicates with a Flask API server (`api_server.py`) that:
- Accepts projection parameters via HTTP GET requests
- Runs the Python projection scripts
- Returns chart images as base64-encoded strings
- Handles CORS for cross-origin requests

## Development

### Project Structure

```
frontend/
├── src/
│   ├── app/
│   │   ├── api.service.ts          # API communication service
│   │   ├── app.component.ts        # Main app component
│   │   ├── projection-form/        # Form component for inputs
│   │   └── chart-display/          # Chart display component
│   ├── styles.css                  # Global styles with Tailwind
│   └── main.ts                     # App bootstrap
├── .postcssrc.json                 # PostCSS config for Tailwind
└── package.json                    # Dependencies and scripts
```

### Key Components

- **ApiService**: Handles HTTP requests to the backend
- **ProjectionFormComponent**: Form for user inputs with validation
- **ChartDisplayComponent**: Displays and allows download of charts
- **AppComponent**: Main container with routing logic

## Backend Requirements

Ensure the Python backend is running:
```bash
python api_server.py
```

The API server should be available at `http://localhost:5001`.

## Technologies Used

- **Angular 17**: Modern frontend framework
- **Tailwind CSS**: Utility-first CSS framework
- **TypeScript**: Type-safe JavaScript
- **RxJS**: Reactive programming for API calls
- **PostCSS**: CSS processing with Tailwind
