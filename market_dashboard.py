import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pytz
import logging
import time
from functools import lru_cache

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
            logger.info(f"Installing {package}")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def calculate_returns(data, start_date):
    """Calculate percentage return from start date to present"""
    try:
        # Validate input data
        if not isinstance(data, pd.DataFrame):
            logger.warning("Invalid data type provided to calculate_returns")
            return 0.0
            
        if data.empty:
            logger.warning("Empty data frame provided to calculate_returns")
            return 0.0
            
        if 'Close' not in data.columns:
            logger.warning("Data frame missing 'Close' column")
            return 0.0

        # Convert start_date to timezone-aware datetime
        try:
            start_date = pd.Timestamp(start_date).tz_localize('America/New_York')
        except Exception as e:
            logger.error(f"Error converting start_date: {str(e)}")
            return 0.0
        
        # Ensure data index is timezone-aware
        try:
            if data.index.tz is None:
                data.index = data.index.tz_localize('America/New_York')
        except Exception as e:
            logger.error(f"Error localizing timezone: {str(e)}")
            return 0.0
        
        # Sort data by index
        try:
            data = data.sort_index()
        except Exception as e:
            logger.error(f"Error sorting data: {str(e)}")
            return 0.0
        
        # Get the first price after start_date
        try:
            mask = data.index >= start_date
            if not any(mask):
                logger.warning(f"No data available after {start_date}")
                return 0.0
                
            # Get the first available price after start_date
            start_price = data.loc[mask].iloc[0]['Close']
            end_price = data.iloc[-1]['Close']
            
            if pd.isna(start_price) or pd.isna(end_price):
                logger.error("NaN values found in price data")
                return 0.0
                
            if start_price == 0:
                logger.error("Start price is zero, cannot calculate returns")
                return 0.0
                
            return_value = (end_price / start_price - 1) * 100
            logger.info(f"Calculated return: {return_value:.2f}%")
            return return_value
        except IndexError as e:
            logger.error(f"IndexError in calculate_returns: {str(e)}")
            return 0.0
        except Exception as e:
            logger.error(f"Unexpected error in calculate_returns: {str(e)}")
            return 0.0
    except Exception as e:
        logger.error(f"Error calculating returns: {str(e)}")
        return 0.0

# Cache market data for 5 minutes
@st.cache_data(ttl=300)
def get_market_data():
    """Fetch data for all indices"""
    try:
        logger.info("Fetching market data...")
        
        # Set a shorter period to ensure we get data
        period = "1y"
        interval = "1d"  # Daily data
        
        # Initialize empty dataframes
        russell_data = pd.DataFrame()
        agg_data = pd.DataFrame()
        acwx_data = pd.DataFrame()
        
        # Fetch Russell 3000 data
        try:
            # Try multiple tickers for Russell 3000 with retries
            tickers = ["VTI", "SPY", "IVV"]  # Reduced number of tickers
            max_retries = 2  # Reduced retries
            retry_delay = 1  # Reduced delay
            
            for ticker in tickers:
                logger.info(f"Trying ticker {ticker} for Russell 3000")
                for attempt in range(max_retries):
                    try:
                        russell = yf.Ticker(ticker)
                        russell_data = russell.history(period=period, interval=interval)
                        if not russell_data.empty and len(russell_data) > 10:
                            logger.info(f"Successfully fetched Russell 3000 data using {ticker}")
                            break
                        else:
                            logger.warning(f"Empty or insufficient data for {ticker}, attempt {attempt + 1}/{max_retries}")
                            if attempt < max_retries - 1:
                                time.sleep(retry_delay)
                    except Exception as e:
                        logger.error(f"Error fetching {ticker}: {str(e)}")
                        if attempt < max_retries - 1:
                            time.sleep(retry_delay)
                if not russell_data.empty and len(russell_data) > 10:
                    break
            
            if not isinstance(russell_data, pd.DataFrame):
                logger.error("Russell 3000 data is not a DataFrame")
                russell_data = pd.DataFrame()
            elif russell_data.empty:
                logger.error("Russell 3000 data is empty after trying all tickers")
                st.error("Failed to fetch Russell 3000 data")
            elif 'Close' not in russell_data.columns:
                logger.error("Russell 3000 data missing 'Close' column")
                st.error("Russell 3000 data is invalid")
        except Exception as e:
            logger.error(f"Error fetching Russell 3000 data: {str(e)}")
            russell_data = pd.DataFrame()
            
        # Fetch AGG data
        try:
            # Try multiple tickers for Barclays US Aggregate with retries
            tickers = ["BND", "AGG"]  # Reduced number of tickers
            max_retries = 2  # Reduced retries
            retry_delay = 1  # Reduced delay
            
            for ticker in tickers:
                logger.info(f"Trying ticker {ticker} for Barclays US Aggregate")
                for attempt in range(max_retries):
                    try:
                        agg = yf.Ticker(ticker)
                        agg_data = agg.history(period=period, interval=interval)
                        if not agg_data.empty and len(agg_data) > 10:
                            logger.info(f"Successfully fetched Barclays US Aggregate data using {ticker}")
                            break
                        else:
                            logger.warning(f"Empty or insufficient data for {ticker}, attempt {attempt + 1}/{max_retries}")
                            if attempt < max_retries - 1:
                                time.sleep(retry_delay)
                    except Exception as e:
                        logger.error(f"Error fetching {ticker}: {str(e)}")
                        if attempt < max_retries - 1:
                            time.sleep(retry_delay)
                if not agg_data.empty and len(agg_data) > 10:
                    break
            
            if not isinstance(agg_data, pd.DataFrame):
                logger.error("AGG data is not a DataFrame")
                agg_data = pd.DataFrame()
            elif agg_data.empty:
                logger.error("AGG data is empty after trying all tickers")
                st.error("Failed to fetch Barclays US Aggregate data")
            elif 'Close' not in agg_data.columns:
                logger.error("AGG data missing 'Close' column")
                st.error("AGG data is invalid")
        except Exception as e:
            logger.error(f"Error fetching AGG data: {str(e)}")
            agg_data = pd.DataFrame()
            
        # Fetch ACWX data
        try:
            # Try multiple tickers for MSCI ACWI ex US with retries
            tickers = ["ACWX", "VXUS"]  # Reduced number of tickers
            max_retries = 2  # Reduced retries
            retry_delay = 1  # Reduced delay
            
            for ticker in tickers:
                logger.info(f"Trying ticker {ticker} for MSCI ACWI ex US")
                for attempt in range(max_retries):
                    try:
                        acwx = yf.Ticker(ticker)
                        acwx_data = acwx.history(period=period, interval=interval)
                        if not acwx_data.empty and len(acwx_data) > 10:
                            logger.info(f"Successfully fetched MSCI ACWI ex US data using {ticker}")
                            break
                        else:
                            logger.warning(f"Empty or insufficient data for {ticker}, attempt {attempt + 1}/{max_retries}")
                            if attempt < max_retries - 1:
                                time.sleep(retry_delay)
                    except Exception as e:
                        logger.error(f"Error fetching {ticker}: {str(e)}")
                        if attempt < max_retries - 1:
                            time.sleep(retry_delay)
                if not acwx_data.empty and len(acwx_data) > 10:
                    break
            
            if not isinstance(acwx_data, pd.DataFrame):
                logger.error("ACWX data is not a DataFrame")
                acwx_data = pd.DataFrame()
            elif acwx_data.empty:
                logger.error("ACWX data is empty after trying all tickers")
                st.error("Failed to fetch MSCI ACWI ex US data")
            elif 'Close' not in acwx_data.columns:
                logger.error("ACWX data missing 'Close' column")
                st.error("ACWX data is invalid")
        except Exception as e:
            logger.error(f"Error fetching ACWX data: {str(e)}")
            acwx_data = pd.DataFrame()
            
        return russell_data, agg_data, acwx_data
        
    except Exception as e:
        logger.error(f"Unexpected error in get_market_data: {str(e)}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

# Cache the performance chart for 5 minutes
@st.cache_data(ttl=300)
def create_performance_chart(russell_data, agg_data, acwx_data, year_start):
    """Create a line chart showing all indices' performance as percentage change"""
    try:
        # Validate input data
        if not isinstance(russell_data, pd.DataFrame) or not isinstance(agg_data, pd.DataFrame) or not isinstance(acwx_data, pd.DataFrame):
            logger.error("Invalid data type provided to create_performance_chart")
            return go.Figure()
            
        if russell_data.empty and agg_data.empty and acwx_data.empty:
            logger.warning("No data available for performance chart")
            st.warning("No data available for performance chart")
            return go.Figure()

        # Convert year_start to timezone-aware datetime
        try:
            year_start = pd.Timestamp(year_start).tz_localize('America/New_York')
        except Exception as e:
            logger.error(f"Error converting year_start: {str(e)}")
            return go.Figure()
        
        fig = go.Figure()
        
        # Helper function to calculate percentage change
        def calculate_percentage_change(data, start_date):
            if not isinstance(data, pd.DataFrame):
                logger.warning("Invalid data type in calculate_percentage_change")
                return pd.Series()
                
            if data.empty:
                logger.warning("Empty data frame in calculate_percentage_change")
                return pd.Series()
                
            if 'Close' not in data.columns:
                logger.warning("Data frame missing 'Close' column in calculate_percentage_change")
                return pd.Series()
            
            try:
                # Ensure data index is timezone-aware
                if data.index.tz is None:
                    data.index = data.index.tz_localize('America/New_York')
                
                # Sort data by index
                data = data.sort_index()
                
                # Get the first price after start_date
                mask = data.index >= start_date
                if not any(mask):
                    logger.warning(f"No data available after {start_date}")
                    return pd.Series()
                
                # Get the first available price after start_date
                start_price = data.loc[mask].iloc[0]['Close']
                if pd.isna(start_price):
                    logger.error("NaN value found in start price")
                    return pd.Series()
                    
                if start_price == 0:
                    logger.error("Start price is zero, cannot calculate percentage change")
                    return pd.Series()
                
                # Calculate percentage change from start date
                return ((data['Close'] / start_price - 1) * 100)
            except IndexError as e:
                logger.error(f"IndexError in calculate_percentage_change: {str(e)}")
                return pd.Series()
            except Exception as e:
                logger.error(f"Unexpected error in calculate_percentage_change: {str(e)}")
                return pd.Series()
        
        # Add zero line
        fig.add_hline(y=0, line_width=2, line_dash="solid", line_color="black")
        
        # Add each index to the chart only if we have data
        if not russell_data.empty:
            russell_pct = calculate_percentage_change(russell_data, year_start)
            if not russell_pct.empty and len(russell_pct) > 0:
                try:
                    last_value = russell_pct.iloc[-1]
                    if not pd.isna(last_value):
                        fig.add_trace(go.Scatter(
                            x=russell_pct.index,
                            y=russell_pct.values,
                            mode='lines',
                            name='Russell 3000',
                            line=dict(width=2)
                        ))
                        # Add annotation for the last value
                        fig.add_annotation(
                            x=russell_pct.index[-1],
                            y=last_value,
                            text=f'{last_value:.1f}%',
                            showarrow=False,
                            xanchor='left',
                            yanchor='middle',
                            xshift=10
                        )
                except IndexError as e:
                    logger.error(f"IndexError adding Russell 3000 to chart: {str(e)}")
                except Exception as e:
                    logger.error(f"Unexpected error adding Russell 3000 to chart: {str(e)}")
                
        if not acwx_data.empty:
            acwx_pct = calculate_percentage_change(acwx_data, year_start)
            if not acwx_pct.empty and len(acwx_pct) > 0:
                try:
                    last_value = acwx_pct.iloc[-1]
                    if not pd.isna(last_value):
                        fig.add_trace(go.Scatter(
                            x=acwx_pct.index,
                            y=acwx_pct.values,
                            mode='lines',
                            name='MSCI ACWI ex US',
                            line=dict(width=2)
                        ))
                        # Add annotation for the last value
                        fig.add_annotation(
                            x=acwx_pct.index[-1],
                            y=last_value,
                            text=f'{last_value:.1f}%',
                            showarrow=False,
                            xanchor='left',
                            yanchor='middle',
                            xshift=10
                        )
                except IndexError as e:
                    logger.error(f"IndexError adding ACWX to chart: {str(e)}")
                except Exception as e:
                    logger.error(f"Unexpected error adding ACWX to chart: {str(e)}")
                
        if not agg_data.empty:
            agg_pct = calculate_percentage_change(agg_data, year_start)
            if not agg_pct.empty and len(agg_pct) > 0:
                try:
                    last_value = agg_pct.iloc[-1]
                    if not pd.isna(last_value):
                        fig.add_trace(go.Scatter(
                            x=agg_pct.index,
                            y=agg_pct.values,
                            mode='lines',
                            name='Barclays US Aggregate',
                            line=dict(width=2)
                        ))
                        # Add annotation for the last value
                        fig.add_annotation(
                            x=agg_pct.index[-1],
                            y=last_value,
                            text=f'{last_value:.1f}%',
                            showarrow=False,
                            xanchor='left',
                            yanchor='middle',
                            xshift=10
                        )
                except IndexError as e:
                    logger.error(f"IndexError adding AGG to chart: {str(e)}")
                except Exception as e:
                    logger.error(f"Unexpected error adding AGG to chart: {str(e)}")

        if len(fig.data) == 0:
            logger.warning("No data available for the selected time period")
            st.warning("No data available for the selected time period")
            return go.Figure()

        fig.update_layout(
            title='Market Performance (YTD) - Percentage Change',
            xaxis_title='Date',
            yaxis_title='Percentage Change (%)',
            height=500,
            showlegend=True,
            yaxis=dict(
                tickformat='.1f',
                ticksuffix='%',
                gridwidth=1,
                zerolinewidth=2
            ),
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01
            ),
            margin=dict(r=100)  # Add right margin to accommodate annotations
        )
        return fig
    except Exception as e:
        logger.error(f"Error creating performance chart: {str(e)}")
        st.error(f"Error creating performance chart: {str(e)}")
        return go.Figure()

def main():
    try:
        # Install requirements if needed
        install_requirements()

        # Set page config
        st.set_page_config(page_title="Market Returns Dashboard", layout="wide")

        # Title
        st.title("Market Returns Dashboard")

        # Get data
        russell_data, agg_data, acwx_data = get_market_data()

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

        # Calculate returns for ACWX
        acwx_ytd = calculate_returns(acwx_data, year_start)
        acwx_mtd = calculate_returns(acwx_data, month_start)
        acwx_qtd = calculate_returns(acwx_data, quarter_start)

        # Calculate returns for AGG
        agg_ytd = calculate_returns(agg_data, year_start)
        agg_mtd = calculate_returns(agg_data, month_start)
        agg_qtd = calculate_returns(agg_data, quarter_start)

        # Display Russell 3000 returns
        st.subheader("Russell 3000 Index Returns")
        if not russell_data.empty:
            last_update = russell_data.index[-1].strftime("%Y-%m-%d %H:%M:%S")
            st.caption(f"Data last updated: {last_update}")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Year-to-Date Return", f"{russell_ytd:.2f}%")
        with col2:
            st.metric("Quarter-to-Date Return", f"{russell_qtd:.2f}%")
        with col3:
            st.metric("Month-to-Date Return", f"{russell_mtd:.2f}%")

        # Display ACWX returns
        st.subheader("MSCI ACWI ex US Index Returns")
        if not acwx_data.empty:
            last_update = acwx_data.index[-1].strftime("%Y-%m-%d %H:%M:%S")
            st.caption(f"Data last updated: {last_update}")
        col4, col5, col6 = st.columns(3)
        with col4:
            st.metric("Year-to-Date Return", f"{acwx_ytd:.2f}%")
        with col5:
            st.metric("Quarter-to-Date Return", f"{acwx_qtd:.2f}%")
        with col6:
            st.metric("Month-to-Date Return", f"{acwx_mtd:.2f}%")

        # Display AGG returns
        st.subheader("Barclays US Aggregate Bond Index Returns")
        if not agg_data.empty:
            last_update = agg_data.index[-1].strftime("%Y-%m-%d %H:%M:%S")
            st.caption(f"Data last updated: {last_update}")
        col7, col8, col9 = st.columns(3)
        with col7:
            st.metric("Year-to-Date Return", f"{agg_ytd:.2f}%")
        with col8:
            st.metric("Quarter-to-Date Return", f"{agg_qtd:.2f}%")
        with col9:
            st.metric("Month-to-Date Return", f"{agg_mtd:.2f}%")

        # Display performance chart
        fig = create_performance_chart(russell_data, agg_data, acwx_data, year_start)
        st.plotly_chart(fig, use_container_width=True)

        # Add information about the indices
        st.subheader("About the Indices")
        st.write("""
        - **Russell 3000 Index**: A market-capitalization-weighted equity index that tracks 3,000 of the largest U.S.-traded stocks, 
        representing about 98% of the investable U.S. equity market. The index is maintained by FTSE Russell.

        - **MSCI ACWI ex US Index**: A market-capitalization-weighted index that captures large and mid-cap representation across 22 of 23 
        Developed Markets countries (excluding the US) and 24 Emerging Markets countries. The index covers approximately 85% of the global 
        equity opportunity set outside the US.

        - **Barclays US Aggregate Bond Index**: A broad-based flagship benchmark that measures the investment grade, 
        US dollar-denominated, fixed-rate taxable bond market. The index includes Treasuries, government-related and corporate securities, 
        MBS (agency fixed-rate and hybrid ARM pass-throughs), ABS, and CMBS.
        """)
    except Exception as e:
        logger.error(f"Error in main function: {str(e)}")
        st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main() 