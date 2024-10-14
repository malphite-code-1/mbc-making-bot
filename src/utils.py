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

