# statarbpair

This repository contains the code and configuration files for the **statarbpair** project. 

## Project Overview

The **statarbpair** project is designed to analyze historical stock data and identify statistically significant arbitrage opportunities. The project involves the following key components:

1. **Data Collection**: 
   - Collects historical stock data from the Yahoo Finance API (`yfinance`) for the Nifty 50 stocks. 

2. **Analysis**:
   - Uses statistical algorithms to identify pairs of stocks that are likely to exhibit mean-reverting behavior, which can be exploited for arbitrage.
   - Analyzes the correlation between stocks to identify pairs with high correlation.
   - Performs stationarity tests on the spread between correlated stock pairs to ensure they are suitable for arbitrage.

3. **Signal Generation**:
   - Calculates buy and sell signals based on the spread between stock pairs.
   - Generates trading signals indicating when to buy one stock and sell another based on statistical analysis.

4. **Data**:
   - The analysis is performed on 5 years of historical closing data for the Nifty 50 stocks.

## Getting Started

### Prerequisites



- Docker
- Docker Compose

### Installation


   ```sh
   git clone https://github.com/Vasanth-96/statarbpair.git
   cd statarbpair
   docker-compose up --build
   ```
### route to open

   ```sh
   http://127.0.0.1:8000/stocks/analyze_stocks/
   ```
   
### note
please wait atleast 1 min after opening this link since for the first time it takes time then after the results are stored in cache.

