# ######################################################################
# CHANNEL HEADERS
# ######################################################################

HEADER_ORDERBOOK = "book"
HEADER_QUOTE = "quote"
HEADER_TRADE = "trades"


# ######################################################################
# METHODS
# ######################################################################

def build_channel(header, instrument, interval=None, group=None, depth=None):

    content = {"channel": header,
               "instrument": instrument,
               "group": str(group),
               "depth": str(depth),
               "interval": str(interval)}

    if not interval:
        del content["interval"]

    if not group:
        del content["group"]

    if not depth:
        del content["depth"]

    return '.'.join([content[k] for k in content])




