import streamlit as st
import os
from alpha_vantage.timeseries import TimeSeries
import pandas as pd
import matplotlib.pyplot as plt
import base64
#from ap4 import generate
import requests
from datetime import datetime, timedelta
from openai import OpenAI
ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')
NEWS_API_KEY = os.getenv('NEWS_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

client = OpenAI(api_key=OPENAI_API_KEY)
def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    return encoded_string

# Initialize Alpha Vantage TimeSeries
ts = TimeSeries(key=ALPHA_VANTAGE_API_KEY, output_format='pandas')
def generate(encoded_image):
    return "TCS stock price was trending upwards in the last 10 days. The stock price started rising from 1.24 on 2024-02-17 and reached a peak of 1.4 on 2024-02-29. The stock price then started declining and reached a low of 1.25 on 2024-03-05. Based on the recent trend, it is not advisable to buy this stock as the stock price is declining."
def fetch_stock_data(symbol):
    """Fetches the intra-day stock prices of the given symbol."""
    try:
        data, _ = ts.get_intraday(symbol=symbol, interval='60min', outputsize='full')
        return data
    except Exception as e:
        st.error(f"Failed to fetch stock data: {e}")
        return pd.DataFrame()

def plot_stock_data(data, title, filename):
    """Plots the stock data and displays it in the Streamlit app."""
    plt.figure(figsize=(10, 6))
    plt.plot(data['4. close'])
    plt.title(title)
    plt.xlabel('Time')
    plt.ylabel('Stock Price')
    plt.xticks(rotation=45)
    plt.tight_layout()
    image_path = f"{stock_symbol}_{title.replace(' ', '_')}.png"
    plt.savefig(image_path)
    plt.close()
    encoded_image = encode_image_to_base64(image_path)

    # Get analysis text
    analysis_text = generate(encoded_image)  # Make sure this is adapted to return text
    
    # Display the plot
    st.image(image_path, caption=analysis_text)
    return analysis_text

import requests
from datetime import datetime, timedelta

def fetch_news(query):
    """
    Fetch news articles from NewsAPI for a specific query within the last 7 days.

    Parameters:
    - api_key (str): Your NewsAPI API key.
    - query (str): The query term or phrase.

    Returns:
    - dict: The JSON response from the NewsAPI.
    """
    # Calculate the 'to_date' as the current date and 'from_date' as 7 days before
    to_date = datetime.now()
    from_date = to_date - timedelta(days=1)
    
    # Format dates as YYYY-MM-DD
    to_date_str = to_date.strftime('%Y-%m-%d')
    from_date_str = from_date.strftime('%Y-%m-%d')

    # Base URL for the NewsAPI Everything endpoint
    base_url = "https://newsapi.org/v2/everything"
    
    # Parameters for the API request
    params = {
        "q": query,
        "from": from_date_str,
        "to": to_date_str,
        "apiKey": NEWS_API_KEY
    }
    
    # Make the GET request to the NewsAPI
    response = requests.get(base_url, params=params)
    
    # Check if the request was successful
    if response.status_code == 200:
        return response.json()  # Return the JSON response
    else:
        return {"error": "Failed to fetch data", "status_code": response.status_code}



# Streamlit UI
st.title('Stock Data Visualization and Trading Decision Helper')
a_text=""
stock_symbol = st.text_input('Enter Stock Symbol (e.g., TCS.BSE):', '')

# Trading decision fields
trading_decision = st.radio("Would you like to buy or sell?", ('Buy', 'Sell'))

if trading_decision == 'Buy':
    investment_term = st.selectbox('Select investment term:', ('Long term', 'Medium term', 'Short term'))
    risk_preference = st.selectbox('Select risk preference:', ('High risk', 'Low risk'))
    submit_buy = st.button('Submit Buy')
elif trading_decision == 'Sell':
    cost_price = st.number_input('Enter cost price:', value=0.0, format='%f')
    risk_preference = st.selectbox('Select risk preference:', ('High risk', 'Low risk'))
    submit_sell = st.button('Submit Sell')

if stock_symbol:
    if (trading_decision == 'Buy' and submit_buy) or (trading_decision == 'Sell' and submit_sell):
        stock_data = fetch_stock_data(stock_symbol)
        if not stock_data.empty:
            # Visualize for different timeframes
            for timeframe, title in [('1D', 'Last Day'), ('5D', 'Last 5 Days'), ('7D', 'Last Week')]:
                st.subheader(f'{title} Visualization')
                # Assuming 'timeframe_data' needs to be derived from 'stock_data'
                # You would need to implement logic to filter 'stock_data' based on 'timeframe'
                # For simplicity, I'm using 'stock_data' directly here
                if not stock_data.empty:
                    a_text+=f"analysis for {title} stock : "+plot_stock_data(stock_data, f'{title} Stock Price for {stock_symbol}', f'{stock_symbol}_{title}')
            
                else:
                    st.write(f"No data available for {title}.")
            news=fetch_news(stock_symbol)
            news_agent=client.chat.completions.create(
                model="gpt-3.5-turbo-16k",
                messages=[{"role":"system","content":f" You are a stock researcher. Use the news information of the last 7 days provided to you and summarize and respond your analysis for the particular stock : {stock_symbol}."},
                                    {"role":"user","content":f"These are the news information of the last 7 days : {news} "}],
                                    temperature=0)
            response_news=news_agent.choices[0].message.content
            st.subheader("news analysis")
            st.write(response_news)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role":"system","content":" You are a stock researcher. Use the analysis provided by me for different time frames to provide an opinion on what desicion should i take regarding a share do not ask user to ask a real person or a financial advisors"},
                          {"role":"user","content":f"These are the analysis of the chart : {a_text} and this is a news analysis for the news related to the stock : {response_news}"}],
                temperature=0)
            st.subheader(response.choices[0].message.content)
        else:
            st.write("No data found for the given stock symbol.")
