import json
import websocket
import time
import threading
import copy

from typing import Callable

# new imports
import source.features.data as data
import source.features.session as session
from source.support.settings import DERIBIT_WSS_URL

WEBSOCKET_DELAY = 0.5


# ######################################################################
# DERIBIT CLIENT
# ######################################################################

class DeribitChannelClient(object):

    def __init__(self,
                 key: str = None,
                 secret: str = None,
                 message_handler: Callable = None,
                 open_handler: Callable = None,
                 error_handler: Callable = None,
                 close_handler: Callable = None,
                 auto_start: bool = True):

        # Uri
        self.__url = DERIBIT_WSS_URL

        # Websocket properties
        # self.__wss = None
        self.__ws = None
        self.heartbeat = 5

        # Deribit (current) channels
        # these are already subscribed
        self.__channels = []

        # Deribit channels that are not yet subscribed
        # to update the update: self.__execute()
        self.__pending_channels = []

        # Features
        #self.__authentication = AuthManager(wss_url=self.__url, key=key, secret=secret)

        # Setting up delegates
        self.open_handler = open_handler or self.on_open
        self.message_handler = message_handler or self.on_message
        self.error_handler = error_handler or self.on_error
        self.close_handler = close_handler or self.on_close

        # Start a websocket thread in the background
        self.start(auto_start=auto_start)

    # ##################################################################
    # PROPERTIES
    # ##################################################################

    #@property
    #def authentication(self):
    #    return self.__authentication

    #@property
    #def auth(self):
    #    msg = self.authentication.login_message()
    #   return json.dumps(msg)

    @property
    def websocket(self):
        if not self.__ws:
            self.__create_websocket()
        return self.__ws

    # ##################################################################
    # WEBSOCKET BASIC OPERATIONS
    # ##################################################################

    def __create_websocket(self):
        websocket.enableTrace(True)
        ws = websocket.WebSocketApp(self.__url,
                                    keep_running=True,
                                    on_message=self.message_handler,
                                    on_error=self.error_handler,
                                    on_close=self.close_handler)
        ws.on_open = self.on_open
        self.__ws = ws

    def open_socket(self):
        if not self.__ws:
            self.__create_websocket()

        self.__ws.on_open = self.subscribe
        self.__ws.run_forever(ping_interval=self.heartbeat)
        time.sleep(0.25)

    def close_socket(self):
        if self.__ws:
            self.__ws.close()

    def start(self, auto_start: bool = False, daemon: bool = True):
        if auto_start:
            thread = threading.Thread(target=self.open_socket, args=())
            thread.daemon = daemon
            thread.start()
        time.sleep(WEBSOCKET_DELAY)

    # ##################################################################
    # DELEGATES
    # ##################################################################

    @staticmethod
    def on_open(ws, **kwargs):
        pass

    @staticmethod
    def on_message(ws, message):
        print(message)

    @staticmethod
    def on_error(ws, error):
        pass

    @staticmethod
    def on_close(ws):
        print("### closed ###")

    # ##################################################################
    # CHANNEL SUBSCRIPTION
    # ##################################################################

    def subscribe(self, channel=None, immediate=True):

        if not channel:
            return None

        if channel not in self.__channels:
            self.__pending_channels.append(channel)

        if immediate:
            self.implement_channels_modifications()

    def unsubscribe(self, channel=None, immediate=True):

        if channel in self.__pending_channels:
            self.__pending_channels.remove(channel)

        if immediate:
            self.implement_channels_modifications()

    def implement_channels_modifications(self):

        try:
            # Formulate a message for websocket
            msg = session.subscription_message(channels=self.__pending_channels)

            # send message through websocket
            self.websocket.send(json.dumps(msg))

            # if successful, update the list of current channels
            self.__channels = copy.deepcopy(self.__pending_channels)

        except KeyboardInterrupt:
            # TODO Some logging required here...
            print("Channel modification failed.")

    # ##################################################################
    # MARKET DATA CHANNELS
    # ##################################################################

    def subscribe_orderbook(self, instrument):

        channel = data.channel_orderbook(instrument=instrument,
                                         interval=100,
                                         depth=None,
                                         group=None)

        self.subscribe(channel, immediate=True)

    def subscribe_trades(self, instrument):

        channel = data.channel_trades(instrument=instrument,
                                      interval=100)

        self.subscribe(channel, immediate=True)

    def subscribe_quotes(self, instrument):

        channel = data.channel_quotes(instrument=instrument)

        self.subscribe(channel, immediate=True)


if __name__ == '__main__':
    import time

    client = DeribitChannelClient()
    time.sleep(0.5)
    client.subscribe_quotes("BTC-PERPETUAL")
    time.sleep(30)
