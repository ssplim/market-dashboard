# Market Returns Dashboard

A Streamlit-based dashboard that displays real-time market returns for major indices including:
- Russell 3000 Index
- Barclays US Aggregate Bond Index
- MSCI ACWI ex US Index

## Features
- Year-to-Date, Quarter-to-Date, and Month-to-Date returns
- Interactive performance charts
- Real-time data updates
- Last update timestamps for each index

## Requirements
- Python 3.8+
- Streamlit
- yfinance
- pandas
- plotly
- pytz

## Installation
1. Clone this repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running Locally
```bash
streamlit run market_dashboard.py
```

## Deployment
This dashboard is designed to be deployed on Streamlit Cloud. The `requirements.txt` file contains all necessary dependencies.

## Data Sources
- Market data is sourced from Yahoo Finance using the yfinance library
- Updates are pulled in real-time when the dashboard is accessed

## Notes
- The dashboard may experience delays during market hours due to high traffic
- Historical data availability depends on Yahoo Finance's data coverage 
