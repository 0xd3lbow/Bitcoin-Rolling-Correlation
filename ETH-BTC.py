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
symbol = 'ETH/USD' 
end_date = datetime.now()
start_date = end_date - pd.DateOffset(days=89)
ethereum_prices = fetch_historical_data(exchange, symbol, start_date, end_date)

bitcoin_symbol = 'BTC/USD'
bitcoin_prices = fetch_historical_data(exchange, bitcoin_symbol, start_date, end_date)

ethereum_prices = ethereum_prices.reindex(bitcoin_prices.index).dropna()

rolling_correlation_ethereum_bitcoin = ethereum_prices.rolling(window=30).corr(bitcoin_prices)

plt.plot(rolling_correlation_ethereum_bitcoin)
plt.title('Rolling 30-day Correlation: ETH-BTC')
plt.xlabel('Date')
plt.ylabel('Correlation')
plt.legend()

date_formatter = DateFormatter('%m-%d')
plt.gca().xaxis.set_major_formatter(date_formatter)

plt.show()
