import ccxt
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from matplotlib.dates import DateFormatter

def fetch_historical_data(exchange, symbol, start_date, end_date):
    exchange = getattr(ccxt, exchange)()
    timeframe = '1d'
    data = []
    current_date = start_date
    while current_date <= end_date:
        try:
            chunk_data = exchange.fetch_ohlcv(symbol, timeframe=timeframe,
                                              since=current_date.timestamp() * 1000)
            data.extend(chunk_data)
            current_date = pd.to_datetime(chunk_data[-1][0], unit='ms') + pd.Timedelta(days=1)
        except ccxt.BaseError as e:
            print(f"An error occurred while fetching data: {e}")
            break

    df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    return df['close']

exchange = 'kraken'
symbol = 'BTC/USD'
end_date = datetime.now()
start_date = end_date - pd.DateOffset(days=89) 
bitcoin_prices = fetch_historical_data(exchange, symbol, start_date, end_date)

gold_symbol = 'GC=F'
gold_prices = yf.download(gold_symbol, start=start_date, end=end_date)['Close']

sp500_symbol = '^SPX'
sp500_prices = yf.download(sp500_symbol, start=start_date, end=end_date)['Close']

dxy_symbol = 'DX-Y.NYB'
dxy_prices = yf.download(dxy_symbol, start=start_date, end=end_date)['Close']

bitcoin_prices = bitcoin_prices.reindex(gold_prices.index).dropna()
gold_prices = gold_prices.reindex(bitcoin_prices.index).dropna()
sp500_prices = sp500_prices.reindex(bitcoin_prices.index).dropna()
dxy_prices = dxy_prices.reindex(bitcoin_prices.index).dropna()

rolling_correlation_gold = bitcoin_prices.rolling(window=30).corr(gold_prices)
rolling_correlation_sp500 = bitcoin_prices.rolling(window=30).corr(sp500_prices)
rolling_correlation_dxy = bitcoin_prices.rolling(window=30).corr(dxy_prices)

plt.plot(rolling_correlation_gold, label='BTC vs. Gold')
plt.plot(rolling_correlation_sp500, label='BTC vs. S&P 500')
plt.plot(rolling_correlation_dxy, label='BTC vs. DXY')
plt.title('Rolling 30-day Correlation: Bitcoin vs Gold, S&P 500, and DXY')
plt.xlabel('Date')
plt.ylabel('Correlation')
plt.legend()

date_formatter = DateFormatter('%m-%d')
plt.gca().xaxis.set_major_formatter(date_formatter)

plt.show()
