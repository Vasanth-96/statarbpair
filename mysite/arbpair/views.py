import os
os.environ['http_proxy'] = 'http://usrname:password@172.31.2.3:8080'
os.environ['https_proxy'] = 'http://usrname:password@172.31.2.3:8080'



#packages
from django.http import JsonResponse, HttpResponse
import pandas as pd
from itertools import combinations
from statsmodels.tsa.stattools import adfuller
import yfinance as yf
import seaborn as sns
import matplotlib.pyplot as plt
import statsmodels.api as sm
from sklearn.decomposition import PCA
import numpy as np
import requests
import io
from datetime import timedelta, date, datetime

#views here
from django.shortcuts import render
from django.core.cache import cache
from datetime import timezone, datetime, time

def get_end_of_day():
    # Get the current date and time in UTC
    now = datetime.now(timezone.utc)
    # Set the time to 3:30 pm
    end_of_day = now.replace(hour=15, minute=30, second=0, microsecond=0)
    
    # If the current time is after 3:30 pm, set end_of_day to the next day's 3:30 pm
    if now.time() > time(15, 30):
        end_of_day += timedelta(days=1)
    
    return end_of_day

def analyze_stocks(request):
    end_of_day = get_end_of_day()

    results = cache.get('stocks')
    if not results:
        try:
            # Fetch the data
            url = 'https://archives.nseindia.com/content/indices/ind_nifty50list.csv'
            df = pd.read_csv(url)
            ser = df["Symbol"]
            tickers = ser.to_list()
            tickers = [symbol + '.NS' for symbol in ser]
            stocks = yf.download(tickers, period="5y", interval="1d")['Adj Close']

            # Drop rows with missing values
            stocks.dropna(inplace=True)

            # Calculate pairwise correlation
            corr_matrix = stocks.corr()

            # Find highly correlated pairs
            correlation_threshold = 0.8
            pairs = []
            for pair in combinations(stocks.columns, 2):
                corr = corr_matrix.loc[pair[0], pair[1]]
                if corr > correlation_threshold:
                    pairs.append(pair)

            # Test for stationarity and analyze the spread
            results = []
            for pair in pairs:
                spread = stocks[pair[0]] - stocks[pair[1]]
                adf_result = adfuller(spread)
                if adf_result[0] < adf_result[4]['1%'] and adf_result[1] < 0.05:
                    spread_mean = spread.mean()
                    spread_std = spread.std()
                    z_score = (spread - spread_mean) / spread_std
                    buy_threshold = -2.0
                    sell_threshold = 2.0
                    buy_signal = (z_score < buy_threshold).any()
                    sell_signal = (z_score > sell_threshold).any()
                    if buy_signal:
                        results.append({'buy_stock': pair[0], 'sell_stock': pair[1]})
                    elif sell_signal:
                        results.append({'buy_stock': pair[1], 'sell_stock': pair[0]})

            # Set the cache timeout until the next 3:30 pm
            cache.set('stocks', results, timeout=(end_of_day - datetime.now(timezone.utc)))
        except Exception as e:
            # Handle exceptions here
            return HttpResponse(f"Error: {str(e)}")

    context = {'results': results}
    return render(request, 'base.html', context)

