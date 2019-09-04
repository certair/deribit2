from source.clients.async_client import DeribitAsyncClient
from source.utilities import grab_event_loop

# Import events
from source.events import *

# Import features
import source.features.data as data

# Import some Deribit specific classes
from source.support.settings import (DEFAULT_KIND,
                                                 DEFAULT_CURRENCY,
                                                 DEFAULT_DEPTH,
                                                 DERIBIT_WSS_URL)


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
        delegate = self.orderbooks
        return self.__sync_wrapper(delegate, instruments=instruments, depth=depth)


if __name__ == '__main__':

    KEY = "_HYDKpRk"
    SECRET = "K27BaSSjCEPDF6Eu1D7kT7ylojt8PgABZyXT758JZIk"

    client = DeribitClient(key=KEY, secret=SECRET)
    instruments = ["BTC-PERPETUAL" for x in range(500)]

    def on_orderbooks(sender, data):
        print(data)

    sig_orderbook_snapshot_received.connect(on_orderbooks)
    res = client.orderbooks(instruments=instruments, depth=10)

