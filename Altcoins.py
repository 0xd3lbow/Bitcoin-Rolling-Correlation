from matplotlib.dates import DateFormatter
import matplotlib.pyplot as plt
from datetime import datetime
import yfinance as yf
import pandas as pd
import ccxt

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
            print(f"An error occurred while fetching data for {symbol}: {e}")
            return None

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

solana_symbol = 'SOL/USD'
solana_prices = fetch_historical_data(exchange, solana_symbol, start_date, end_date)

matic_symbol = 'MATIC/USD'
matic_prices = fetch_historical_data(exchange, matic_symbol, start_date, end_date)

arbitrum_symbol = 'ARB/USD'
arbitrum_prices = fetch_historical_data(exchange, arbitrum_symbol, start_date, end_date)

ldo_symbol = 'LDO/USD'
ldo_prices = fetch_historical_data(exchange, ldo_symbol, start_date, end_date)

if any(x is None for x in [ethereum_prices, bitcoin_prices, solana_prices, matic_prices, arbitrum_prices, ldo_prices]):
    print("One or more symbols failed to fetch historical data. Please check the symbols or try again later.")
    exit()

ethereum_prices = ethereum_prices.reindex(bitcoin_prices.index).dropna()
solana_prices = solana_prices.reindex(bitcoin_prices.index).dropna()
matic_prices = matic_prices.reindex(bitcoin_prices.index).dropna()
arbitrum_prices = arbitrum_prices.reindex(bitcoin_prices.index).dropna()
ldo_prices = ldo_prices.reindex(bitcoin_prices.index).dropna()

rolling_correlation_ethereum_bitcoin = ethereum_prices.rolling(window=30).corr(bitcoin_prices)
rolling_correlation_solana_bitcoin = solana_prices.rolling(window=30).corr(bitcoin_prices)
rolling_correlation_matic_bitcoin = matic_prices.rolling(window=30).corr(bitcoin_prices)
rolling_correlation_arbitrum_bitcoin = arbitrum_prices.rolling(window=30).corr(bitcoin_prices)
rolling_correlation_ldo_bitcoin = ldo_prices.rolling(window=30).corr(bitcoin_prices)

plt.figure(figsize=(10, 6))
plt.plot(rolling_correlation_ethereum_bitcoin, label='ETH-BTC')
plt.plot(rolling_correlation_solana_bitcoin, label='SOL-BTC')
plt.plot(rolling_correlation_matic_bitcoin, label='MATIC-BTC')
plt.plot(rolling_correlation_arbitrum_bitcoin, label='ARB-BTC')
plt.plot(rolling_correlation_ldo_bitcoin, label='LDO-BTC')
plt.title('Rolling 30-day Correlation: ETH-BTC, SOL-BTC, MATIC-BTC, ARB-BTC, and LDO-BTC')
plt.xlabel('Date')
plt.ylabel('Correlation')
plt.legend()

date_formatter = DateFormatter('%m-%d')
plt.gca().xaxis.set_major_formatter(date_formatter)

plt.show()
