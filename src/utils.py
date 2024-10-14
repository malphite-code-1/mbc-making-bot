import logging
import numpy as np
from lbank.old_api import BlockHttpClient
from datetime import datetime, timedelta, timezone


client = BlockHttpClient(
    sign_method="RSA",
    api_key="API_KEY",
    api_secret="API_SECRET",
    base_url="https://www.lbkex.net/",
    log_level=logging.ERROR,
)

pair = "token_usdt"
token_symbol = "token"


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

