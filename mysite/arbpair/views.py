# views.py

import os
from datetime import timedelta, datetime, timezone, time
from django.http import HttpResponse
import pandas as pd
from itertools import combinations
from statsmodels.tsa.stattools import adfuller
import yfinance as yf
from django.shortcuts import render
from django.core.cache import cache  # Cache is still used, but now it uses Redis as backend


def get_end_of_day():
    """Get the time of 3:30 PM today or the next day if it has already passed."""
    now = datetime.now(timezone.utc)
    end_of_day = now.replace(hour=15, minute=30, second=0, microsecond=0)

    if now.time() > time(15, 30):
        end_of_day += timedelta(days=1)

    return end_of_day

def analyze_stocks(request):
    """Analyze stock data and find pairs of stocks for trading signals."""
    end_of_day = get_end_of_day()
    results = cache.get('stocks')  # This will now retrieve from Redis cache

    if not results:
        try:
            # Fetch the data
            url = 'https://archives.nseindia.com/content/indices/ind_nifty50list.csv'
            df = pd.read_csv(url)
            tickers = [symbol + '.NS' for symbol in df["Symbol"]]
            stocks = yf.download(tickers, period="5y", interval="1d")['Adj Close']

            # Drop rows with missing values
            stocks.dropna(inplace=True)

            # Calculate pairwise correlation
            corr_matrix = stocks.corr()

            # Find highly correlated pairs
            correlation_threshold = 0.8
            pairs = [(pair[0], pair[1]) for pair in combinations(stocks.columns, 2)
                     if corr_matrix.loc[pair[0], pair[1]] > correlation_threshold]

            # Test for stationarity and analyze the spread
            results = []
            for pair in pairs:
                spread = stocks[pair[0]] - stocks[pair[1]]
                adf_result = adfuller(spread)

                # Check if the spread is stationary
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

            # Set the cache timeout until the next 3:30 PM
            cache_timeout = int((end_of_day - datetime.now(timezone.utc)).total_seconds())
            cache.set('stocks', results, timeout=cache_timeout)  # Store in Redis cache
        except Exception as e:
            # Handle exceptions and provide an informative error message
            return HttpResponse(f"Error fetching or analyzing stock data: {str(e)}")

    context = {'results': results}
    return render(request, 'base.html', context)
