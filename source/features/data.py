from source.support.sanitizers import *
from source.support.channel_name import build_channel
from source.features.common import message, add_params_to_message
from source.support.types import INTERVAL, PUBLIC_CHANNELS

# ######################################################################
# METHODS
# ######################################################################

METHOD_GET_INSTRUMENTS = "public/get_instruments"
METHOD_GET_ORDER_BOOK = "public/get_order_book"
METHOD_CURRENCIES = "public/get_currencies"
METHOD_INDEX = "public/get_index"

METHOD_SUBSCRIBE = "public/subscribe"

# ######################################################################
# REQUESTS
# ######################################################################

def request_instruments(currency: str, kind: str, expired=False):

    # Sanitize input arguments
    data = sanitize(currency=currency, kind=kind)

    # Build basic message
    msg = message(method=METHOD_GET_INSTRUMENTS)
    params = {"currency": data["currency"], "kind": data["kind"], "expired": expired}
    return add_params_to_message(params, msg)


def request_orderbook(instrument: str, depth: int = None):

    # Sanitize input arguments
    data = sanitize(instrument=instrument, depth=depth)

    # Get basic method call
    msg = message(method=METHOD_GET_ORDER_BOOK)

    # Add parameters
    params = {"instrument_name": data["instrument"], "depth": data["depth"]}
    return add_params_to_message(params, msg)


def request_orderbooks(instruments: list, depth: int = None):
    messages = []
    for ins in instruments:
        messages.append(request_orderbook(ins, depth))
    return messages


def request_currencies():
    msg = message(method=METHOD_CURRENCIES)
    return add_params_to_message({}, msg)


def request_index(currency: str):
    # Sanitize input arguments
    data = sanitize(currency=currency)
    params = {"currency": data["currency"]}
    msg = message(method=METHOD_INDEX)
    return add_params_to_message(params, msg)


# ######################################################################
# CHANNELS
# ######################################################################

def channel_orderbook(instrument: str,
                      interval: int = DEFAULT_INTERVAL,
                      group: int = None,
                      depth: int = None):

    # Sanitize input arguments
    data = sanitize(instrument=instrument, interval=interval,
                    group=group, depth=depth)

    # WARNING: For orderbook modification, the only supported
    # interval is 100ms.
    channel = build_channel(header=PUBLIC_CHANNELS.ORDERBOOK_UPDATES,
                            instrument=data["instrument"],
                            group=data["group"],
                            depth=data["depth"],
                            interval=INTERVAL.STANDARD)
    return channel


def channel_trades(instrument: str, interval: int = None):

    # Sanitize input arguments
    data = sanitize(instrument=instrument, interval=interval)

    # Get (clean) channel name
    channel = build_channel(header=PUBLIC_CHANNELS.TRADES,
                            instrument=data["instrument"],
                            interval=data["interval"])
    return channel


def channel_quotes(instrument: str):

    # Sanitize input arguments
    data = sanitize(instrument=instrument)

    # Get (clean) channel name
    channel = build_channel(header=PUBLIC_CHANNELS.QUOTES.value,
                            instrument=data["instrument"])
    return channel
