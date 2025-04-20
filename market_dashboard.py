import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pytz

def install_requirements():
    """Install required packages if not already installed"""
    import subprocess
    import sys
    requirements = [
        'streamlit==1.32.0',
        'yfinance==0.2.36',
        'pandas==2.2.1',
        'plotly==5.18.0',
        'pytz'
    ]
    for package in requirements:
        try:
            __import__(package.split('==')[0])
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def calculate_returns(data, start_date):
    """Calculate percentage return from start date to present"""
    # Convert start_date to timezone-aware datetime
    start_date = pd.Timestamp(start_date).tz_localize('America/New_York')
    # Get the last price before or on start_date
    start_price = data[data.index <= start_date].iloc[-1]['Close']
    end_price = data.iloc[-1]['Close']
    return (end_price / start_price - 1) * 100

def get_market_data():
    """Fetch data for both indices"""
    russell = yf.Ticker("^RUA")
    agg = yf.Ticker("AGG")
    russell_data = russell.history(period="max")
    agg_data = agg.history(period="max")
    return russell_data, agg_data

def create_performance_chart(russell_data, agg_data, year_start):
    """Create a line chart showing both indices' performance"""
    # Convert year_start to timezone-aware datetime
    year_start = pd.Timestamp(year_start).tz_localize('America/New_York')
    current_year_russell = russell_data[russell_data.index >= year_start]
    current_year_agg = agg_data[agg_data.index >= year_start]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=current_year_russell.index,
        y=current_year_russell['Close'],
        mode='lines',
        name='Russell 3000'
    ))
    fig.add_trace(go.Scatter(
        x=current_year_agg.index,
        y=current_year_agg['Close'],
        mode='lines',
        name='Barclays US Aggregate'
    ))

    fig.update_layout(
        title='Market Performance (YTD)',
        xaxis_title='Date',
        yaxis_title='Index Value',
        height=500
    )
    return fig

def main():
    # Install requirements if needed
    install_requirements()

    # Set page config
    st.set_page_config(page_title="Market Returns Dashboard", layout="wide")

    # Title
    st.title("Market Returns Dashboard")

    # Get data
    russell_data, agg_data = get_market_data()

    # Calculate current date and relevant dates
    current_date = datetime.now()
    year_start = datetime(current_date.year, 1, 1)
    month_start = datetime(current_date.year, current_date.month, 1)
    quarter = (current_date.month - 1) // 3 + 1
    quarter_start = datetime(current_date.year, (quarter - 1) * 3 + 1, 1)

    # Calculate returns for Russell 3000
    russell_ytd = calculate_returns(russell_data, year_start)
    russell_mtd = calculate_returns(russell_data, month_start)
    russell_qtd = calculate_returns(russell_data, quarter_start)

    # Calculate returns for AGG
    agg_ytd = calculate_returns(agg_data, year_start)
    agg_mtd = calculate_returns(agg_data, month_start)
    agg_qtd = calculate_returns(agg_data, quarter_start)

    # Display Russell 3000 returns
    st.subheader("Russell 3000 Index Returns")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Year-to-Date Return", f"{russell_ytd:.2f}%")
    with col2:
        st.metric("Month-to-Date Return", f"{russell_mtd:.2f}%")
    with col3:
        st.metric("Quarter-to-Date Return", f"{russell_qtd:.2f}%")

    # Display AGG returns
    st.subheader("Barclays US Aggregate Bond Index Returns")
    col4, col5, col6 = st.columns(3)
    with col4:
        st.metric("Year-to-Date Return", f"{agg_ytd:.2f}%")
    with col5:
        st.metric("Month-to-Date Return", f"{agg_mtd:.2f}%")
    with col6:
        st.metric("Quarter-to-Date Return", f"{agg_qtd:.2f}%")

    # Display performance chart
    fig = create_performance_chart(russell_data, agg_data, year_start)
    st.plotly_chart(fig, use_container_width=True)

    # Add information about the indices
    st.subheader("About the Indices")
    st.write("""
    - **Russell 3000 Index**: A market-capitalization-weighted equity index that tracks 3,000 of the largest U.S.-traded stocks, 
    representing about 98% of the investable U.S. equity market. The index is maintained by FTSE Russell.

    - **Barclays US Aggregate Bond Index**: A broad-based flagship benchmark that measures the investment grade, 
    US dollar-denominated, fixed-rate taxable bond market. The index includes Treasuries, government-related and corporate securities, 
    MBS (agency fixed-rate and hybrid ARM pass-throughs), ABS, and CMBS.
    """)

if __name__ == "__main__":
    main() 