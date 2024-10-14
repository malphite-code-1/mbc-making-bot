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

