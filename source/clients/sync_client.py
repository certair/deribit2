from source.clients.async_client import DeribitAsyncClient

from source.events import *

from source.support.settings import (DEFAULT_DEPTH)
from source.utilities import grab_event_loop


# Import features


# ######################################################################
# DERIBIT CLIENT
# ######################################################################

class DeribitClient(DeribitAsyncClient):

    def __init__(self,
                 key=None,
                 secret=None):

        super().__init__(key=key, secret=secret)

    # ##################################################################
    # SYNC WRAPPER
    # ##################################################################

    def __sync_wrapper(self, delegate, **kwargs):
        loop = grab_event_loop()
        result = loop.run_until_complete(delegate(**kwargs))
        loop.close()
        return result

    # ##################################################################
    # DATA
    # ##################################################################

    def orderbooks(self, instruments, depth=DEFAULT_DEPTH):
        delegate = super().orderbooks
        return self.__sync_wrapper(delegate, instruments=instruments, depth=depth)


    # ##################################################################
    # SESSION
    # ##################################################################

    # Add missing routes

    # ##################################################################
    # ACCOUNT
    # ##################################################################

    # Add missing routes

    # ##################################################################
    # TRADING
    # ##################################################################

    # Add missing routes



if __name__ == '__main__':

    KEY = "k.."
    SECRET = "s.."

    client = DeribitClient(key=KEY, secret=SECRET)
    instruments = ["BTC-PERPETUAL" for x in range(1)]

    def on_orderbooks(sender, data):
        print(data)

    sig_orderbook_snapshot_received.connect(on_orderbooks)
    res = client.orderbooks(instruments=instruments, depth=10)

