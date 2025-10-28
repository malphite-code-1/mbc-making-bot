import logging
import numpy as np
from lbank.old_api import BlockHttpClient
from datetime import datetime, timedelta, timezone


client = BlockHttpClient(
    sign_method="RSA",
    api_key="API_KEY",
    api_secret="API_SECRET",
    base_url="https://api.lbkex.com/",
    log_level=logging.ERROR,
)

pair = "mbc_usdt"
token_symbol = "mbc"


def get_order_book(symbol):
    """
    Fetch the order book for a given symbol.

    Parameters:
    - symbol: Trading pair symbol (e.g., pair)

    Returns:
    - dict: Order book data
    """
    api_url = "v2/supplement/ticker/bookTicker.do"
    payload = {"symbol": symbol}
    return client.http_request("get", api_url, payload=payload)


def get_buy_price_in_spread():
    order_book = get_order_book(pair)
    ask_price = float(order_book["data"]["askPrice"])
    # Calculate the maximum allowable ask price based on a 2% spread
    max_ask_price = ask_price * 0.98
    return max_ask_price


def get_sell_price_in_spread():
    order_book = get_order_book(pair)
    bid_price = float(order_book["data"]["bidPrice"])
    # Calculate the maximum allowable ask price based on a 2% spread
    max_ask_price = bid_price * 1.02
    return max_ask_price


def place_order(symbol, side, amount, price=None):
    """
    Place an order on the exchange.

    Parameters:
    - symbol: Trading pair symbol (e.g., pair)
    - side: Order side ("buy_maker" or "sell_maker")
    - price: Price at which to place the order
    - amount: Amount of the asset to trade

    Returns:
    - dict: Response from the exchange
    """

    path = "v2/create_order.do"

    payload = {
        "symbol": symbol,
        "type": side,
        "amount": amount,
    }

    if price is not None:
        payload["price"] = price

    return client.http_request("post", path, payload=payload)


def cancel_all_orders(symbol):
    """
    Cancel all orders for a given symbol.

    Parameters:
    - symbol: Trading pair symbol (e.g., pair)

    Returns:
    - dict: Response from the exchange
    """

    path = "v2/supplement/cancel_order_by_symbol.do"
    payload = {"symbol": symbol}
    return client.http_request("POST", path, payload=payload)


def cancel_one_order(symbol, order_id):
    """
    Cancel One order

    Parameters:
    - symbol: Trading pair symbol (e.g., pair)
    - order_id : Order of the id that you need to cancel

    Returns:
    - dict: Response from the exchange
    """
    path = "v2/supplement/cancel_order.do"
    payload = {"symbol": symbol, "orderId": order_id}
    return client.http_request("POST", path, payload=payload)


def cancel_list_of_orders(symbol, order_ids):
    """
    Cancel a List of orders used to not intrrupt the other orders

    Parameters:
    - symbol: Trading pair symbol (e.g., pair)
    - order_ids : List of Order ids that you need to cancel

    """
    if not order_ids:
        return
    for order_id in order_ids:
        print(cancel_one_order(symbol, order_id))
        order_ids.remove(order_id)


def get_current_price(symbol):
    """
    Get the current price for a given symbol.

    Parameters:
    - symbol: Trading pair symbol (e.g., pair)

    Returns:
    - float: Current price of the trading pair
    """
    path = "v2/supplement/ticker/price.do"
    payload = {"symbol": symbol}
    res = client.http_request("GET", path, payload=payload)
    if res["result"] == True:
        current_price = res["data"][0]["price"]
        return float(current_price)
    else:
        raise Exception(
            "Failed to get current price: " + res.get("error", "Unknown error")
        )


def calculate_order_size(
    order_type, volatility, max_order_size, min_order_size, risk_percentage=None
):
    """
    Calculate the order size based on risk management.

    Parameters:
    - order_type: The type of order ('buy' or 'sell').
    - volatility: The current market volatility.
    - max_order_size: The maximum allowed size for an order.
    - min_order_size: The minimum allowed size for an order.
    - risk_percentage: Optional risk percentage of the account balance to use per trade.

    Returns:
    - order_size: The calculated order size.
    """
    current_price = get_current_price(pair)

    # Fetch account balance
    account_balances = fetch_account_balance()

    if order_type == "sell":
        # Use the token_symbol balance for sell orders
        asset_balance = account_balances[token_symbol]["free"]
    elif order_type == "buy":
        # Use the USDT balance for buy orders
        usdt_balance = account_balances["usdt"]["free"]
        # Convert USDT balance to token_symbol
        asset_balance = usdt_balance / current_price

    # Optionally apply a risk percentage if provided
    if risk_percentage is not None:
        risk_amount = asset_balance * risk_percentage
    else:
        risk_amount = asset_balance  # Use the full balance without risk adjustment

    # Ensure max_order_size does not exceed the available balance
    if max_order_size > risk_amount:
        max_order_size = risk_amount

    # Adjust order size based on volatility
    volatility_adjustment = 1 / (volatility + 1)

    # Calculate the raw order size
    raw_order_size = (
        risk_amount * volatility_adjustment / current_price
        if order_type == "buy"
        else risk_amount * volatility_adjustment
    )

    # Ensure the order size is within defined limits
    order_size = max(min(raw_order_size, max_order_size), min_order_size)

    return order_size


def get_dynamic_sleep_time(volatility):
    """
    Get dynamic sleep time based on market volatility.

    Parameters:
    - volatility: Current market volatility

    Returns:
    - int: Dynamic sleep time in seconds
    """

    # Initialize parameters
    base_sleep_time = 8  # Base sleep time in seconds
    max_sleep_time = 20  # Maximum sleep time in seconds
    min_sleep_time = 1  # Minimum sleep time in seconds

    # Adjust sleep time based on volatility
    if volatility > 0.05:  # High volatility threshold
        sleep_time = base_sleep_time / 2
    elif volatility < 0.02:  # Low volatility threshold
        sleep_time = base_sleep_time * 2
    else:
        sleep_time = base_sleep_time

    # Ensure sleep time is within limits
    sleep_time = max(min(sleep_time, max_sleep_time), min_sleep_time)

    return sleep_time


def calculate_percentage_change(initial_balance, current_balance):
    change = ((current_balance - initial_balance) / initial_balance) * 100
    return change


def fetch_historical_prices(period):
    """
    Fetch historical prices for a given period.

    Parameters:
    - period: Number of minutes of historical data to fetch

    Returns:
    - list: Historical price data
    """
    path = "v2/kline.do"
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(minutes=period)

    # Convert dates to timestamps in seconds
    end_timestamp = int(end_date.timestamp())
    start_timestamp = int(start_date.timestamp())

    payload = {
        "symbol": pair,
        "type": "minute1",
        "size": period,
        "time": start_timestamp,
    }
    return client.http_request("get", api_url, payload=payload)


def calculate_price_changes(price_data):
    """
    Calculate price changes from historical price data.

    Parameters:
    - price_data: List of historical prices

    Returns:
    - numpy.array: Array of price changes
    """
    # Calculate price changes from historical price data
    prices = np.array(price_data)
    price_changes = np.diff(prices) / prices[:-1]
    return price_changes


def calculate_standard_deviation(price_changes):
    """
    Calculate the standard deviation of price changes.

    Parameters:
    - price_changes: Array of price changes

    Returns:
    - float: Standard deviation of price changes
    """
    return np.std(price_changes)


def get_dynamic_volatilit(period):
    """
    Determain the volatilit of the pair through a period of time.
    Keeps increasing the period if the volatilit is too low.

    Parameters:
    - period: Number of minutes

    Returns:
    - float: volatilit
    """
    price_data = fetch_historical_prices(period)  # In minutes
    price_changes = calculate_price_changes(price_data)
    current_volatility = calculate_standard_deviation(price_changes)

    if current_volatility == 0:
        period += 60
        get_dynamic_volatilit(period)

    return current_volatility


def calculate_order_sizes(total_order_size, num_orders):
    order_sizes = []
    remaining_percentage = 0.70
    first_order_size = total_order_size * 0.30

    order_sizes.append(first_order_size)

    for i in range(1, num_orders):
        next_order_size = total_order_size * (remaining_percentage * 0.3)
        order_sizes.append(next_order_size)
        remaining_percentage *= 0.7

    # Return a list of order Sizes where the first size is the larges
    return order_sizes
    # Return a list of order Sizes where the last size is the larges
    # return order_sizes.reverse()


def get_price_step_percentage(order_num, base_price_step_percentage):
    if order_num < 9:
        return base_price_step_percentage
    elif order_num < 12:
        return base_price_step_percentage * 2.5
    else:
        return base_price_step_percentage * 4


def fetch_account_balance():
    """
    Fetch account balance for specified assets.

    Returns:
    - dict: Account balances for targeted assets
    """
    path = "v2/supplement/user_info_account.do"
    res = client.http_request("POST", path)
    if res["result"] == "true":
        balances = res["data"]["balances"]
        targeted_assets = {"usdt": None, token_symbol: None}
        for balance in balances:
            if balance["asset"] in targeted_assets:
                targeted_assets[balance["asset"]] = {
                    "free": float(balance["free"]),
                    "locked": float(balance["locked"]),
                }
            if all(value is not None for value in targeted_assets.values()):
                break
        return targeted_assets
    else:
        raise Exception(
            "Failed to fetch account balances: " + res.get("msg", "Unknown error")
        )


def calculate_percentage_change(initial_balance, current_balance):
    change = ((current_balance - initial_balance) / initial_balance) * 100
    return change


def get_current_orders():
    """
    Get the current pending orders

    Returns:
    -

    """
    path = "v2/supplement/orders_info_no_deal.do"
    payload = {"symbol": pair, "current_page": "1", "page_length": "200"}
    res = client.http_request("POST", path, payload=payload)
    return res


def get_num_of_orders():
    list_of_orders = get_current_orders()["data"]["orders"]
    return len(list_of_orders)
