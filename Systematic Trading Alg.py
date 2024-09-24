import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# List of stock tickers
fortune_100_tickers = ['MSFT', 'INTC', 'LMT', 'DFEN', 'TSLA', 'BA', 'RTX', 'NVDA', 'AAPL',]

# Define risk management parameters
initial_capital = 5000  # Starting capital
risk_per_trade = 0.08  # Risk 8% of capital per trade
stop_loss_pct = 0.12  # Stop-loss at 12% drop from entry price

# Loop through each stock
for ticker in fortune_100_tickers:
    # Download historical data
    stock_data = yf.download(ticker, start='2022-09-01', end='2024-09-23')

    # Calculate 20-day and 50-day Simple Moving Averages (SMA)
    stock_data['SMA20'] = stock_data['Close'].rolling(window=20).mean()
    stock_data['SMA50'] = stock_data['Close'].rolling(window=50).mean()

    # Generate Buy/Sell signals
    stock_data['Signal'] = 0
    stock_data['Signal'][20:] = np.where(stock_data['SMA20'][20:] > stock_data['SMA50'][20:], 1, 0)
    stock_data['Position'] = stock_data['Signal'].diff()

    # Initialize variables for tracking the performance
    cash = initial_capital
    position = 0  # Number of shares held
    entry_price = 0
    profit_loss = 0
    stock_data['Portfolio'] = np.nan  # Track portfolio value over time

    for i in range(len(stock_data)):
        # Buy condition
        if stock_data['Position'][i] == 1:
            amount_to_risk = cash * risk_per_trade
            position_size = amount_to_risk / (stock_data['Close'][i] * stop_loss_pct)
            position = position_size
            entry_price = stock_data['Close'][i]
            cash -= position * entry_price  # Reduce cash by amount spent

        # Sell condition (either signal or stop-loss)
        elif stock_data['Position'][i] == -1 or (position > 0 and stock_data['Close'][i] < entry_price * (1 - stop_loss_pct)):
            cash += position * stock_data['Close'][i]  # Add back cash from the sale
            position = 0  # Reset position

        # Calculate portfolio value
        portfolio_value = cash + (position * stock_data['Close'][i] if position > 0 else 0)
        stock_data['Portfolio'][i] = portfolio_value

    # Plot the stock price, SMA, buy/sell signals, and portfolio value on separate axes
    fig, ax1 = plt.subplots(figsize=(14,7))

    # Stock prices and SMAs on the left y-axis
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Stock Price', color='tab:blue')
    ax1.plot(stock_data.index, stock_data['Close'], label=f'{ticker} Close Price', alpha=0.5, color='tab:blue')
    ax1.plot(stock_data.index, stock_data['SMA20'], label='20-day SMA', alpha=0.75, color='orange')
    ax1.plot(stock_data.index, stock_data['SMA50'], label='50-day SMA', alpha=0.75, color='green')

    # Buy/Sell signals
    ax1.scatter(stock_data[stock_data['Position'] == 1].index, stock_data['SMA20'][stock_data['Position'] == 1],
                marker='^', color='g', label='Buy Signal', lw=3)
    ax1.scatter(stock_data[stock_data['Position'] == -1].index, stock_data['SMA20'][stock_data['Position'] == -1],
                marker='v', color='r', label='Sell Signal', lw=3)

    ax1.legend(loc='upper left')
    ax1.tick_params(axis='y', labelcolor='tab:blue')

    # Portfolio value on the right y-axis
    ax2 = ax1.twinx()
    ax2.set_ylabel('Portfolio Value', color='tab:red')
    ax2.plot(stock_data.index, stock_data['Portfolio'], label='Portfolio Value', linestyle='--', alpha=0.75, color='tab:red')
    ax2.tick_params(axis='y', labelcolor='tab:red')

    fig.tight_layout()
    plt.title(f'Moving Average Crossover Strategy with Risk Management for {ticker}')
    plt.show()




