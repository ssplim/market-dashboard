# Market Returns Dashboard

A Streamlit-based dashboard for tracking market returns across different indices.

## Features
- Real-time market data from Yahoo Finance
- Performance tracking for multiple indices
- Interactive charts and visualizations
- Automatic data updates

## Installation
1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage
Run the dashboard:
```bash
streamlit run market_dashboard.py
```

Access the dashboard at:
- Local: http://localhost:8501
- Network: http://[your-ip]:8501

## Dependencies
- streamlit==1.32.0
- yfinance==0.2.55
- pandas==2.2.1
- plotly==5.18.0
- pytz==2024.1

## Data Sources
- Market data is sourced from Yahoo Finance using the yfinance library
- Updates are pulled in real-time when the dashboard is accessed

## Notes
- The dashboard may experience delays during market hours due to high traffic
- Historical data availability depends on Yahoo Finance's data coverage 
