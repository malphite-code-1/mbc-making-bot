# Market Making Bot

This repository contains the code for a market-making bot that interacts with the LBANK exchange API to provide liquidity for a trading pair. The bot places buy and sell orders at strategic price levels, adjusting for market volatility to profit from the spread.

## Project Structure

- **main.py**: The entry point of the application. It runs the `market_making` function to start the bot.
- **requirements.txt**: Contains the list of Python packages required to run the bot.
- **src/**: Contains the source code for the bot.
  - **market_making.py**: Implements the market-making strategy.
  - **utils.py**: Contains utility functions and API calls to interact with the LBANK exchange.

## Getting Started

To run the market-making bot, follow these steps:

### Prerequisites

- Python 3.8 or higher
- An LBANK account with API access enabled

### Installation

1. Clone the repository:

   ```sh
   git clone https://github.com/MohamadSafi/market-making-bot.git
   cd market-making-bot
   ```

2. Create a virtual environment and activate it:

   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required dependencies:

   ```sh
   pip install -r requirements.txt
   ```

### Configuration

Update `src/utils.py` with your LBANK API credentials:

```python
API_KEY = "your_api_key"
SECRET_KEY = "your_secret_key"
```

Ensure you have added your API keys to interact with the LBANK exchange properly.

### Running the Bot

Run the bot by executing the main script:

```sh
python main.py
```

The bot will continuously run, placing buy and sell orders based on market conditions. To stop the bot, use `Ctrl+C`.

### How the Bot Works

- **market_making.py** contains the core strategy code for the bot. It:

  - Fetches order book data and account balance.
  - Calculates order sizes and price levels.
  - Places multiple buy and sell orders with a defined spread.
  - Adjusts the trading strategy based on market volatility.
  - Pauses or resumes trading based on balance changes to avoid overexposure.

- **utils.py** provides utility functions like:
  - Placing orders (`place_order`)
  - Cancelling orders (`cancel_all_orders`, `cancel_list_of_orders`)
  - Fetching market data (`get_order_book`, `fetch_account_balance`)

### Example Usage

You can customize the bot's behavior by modifying the parameters in `market_making()` in `main.py`. For example:

```python
market_making( max_order_size=100, min_order_size=10, num_orders=10, base_price_step_percentage=0.00009)
```

Adjust `max_order_size`, `min_order_size`, `num_orders`, and `base_price_step_percentage` as per your needs to adapt to different trading pairs and market conditions.

## Contributing

Feel free to fork the repository and submit a pull request if you have improvements or features you would like to add.

## Disclaimer

This code is for educational purposes only. Use it at your own risk, and remember that trading is inherently risky. This bot is not financial advice, and the developers are not responsible for any losses.

## License

This project is licensed under the MIT License.
