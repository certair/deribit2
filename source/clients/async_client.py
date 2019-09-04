import json
import logging
import websockets
import datetime as dt

# Import events
from source.events import *

# Import networking constants
from source.support.networking import *

# Import features
import source.features.data as data
import source.features.session as session
import source.features.account as account
import source.features.trading as trading

from source.utilities import generate_id
from source.features.common import message

# Import some Deribit specific classes
from source.support.settings import (DEFAULT_KIND,
                                     DEFAULT_CURRENCY,
                                     DEFAULT_DEPTH,
                                     DERIBIT_WSS_URL)


# ######################################################################
# ENDPOINTS
# ######################################################################

METHOD_LOGIN = "public/auth"
METHOD_LOGOUT = "private/logout"


# ######################################################################
# DERIBIT CLIENT
# ######################################################################

class DeribitAsyncClient(object):

    def __init__(self,
                 key=None,
                 secret=None):

        self.__id = generate_id()
        self.__url = DERIBIT_WSS_URL
        self.__key = self.parse_key(key=key)
        self.__secret = self.parse_secret(secret=secret)

        # Login management
        self.__is_login = False
        self.__access_token = None
        self.__refresh_token = None
        self.__token_expiry = None

        def handle_signal_login(sender, data=None, websocket=None, **kwargs):
            self.on_deribit_login(sender, data, websocket, **kwargs)

        self.handle_signal_login = handle_signal_login
        sig_login.connect(handle_signal_login)

        logging.debug(f"[{self.id}] Deribit Async client instance created.")

    # ##################################################################
    # PROPERTIES
    # ##################################################################

    @property
    def id(self):
        return self.__id

    @property
    def key(self):
        return self.__key

    @property
    def secret(self):
        return self.__secret

    @property
    def access_token(self):
        if not self.__access_token:
            raise Exception("Access token not available.")
        return self.__access_token

    @property
    def token_expiry(self):
        if self.__token_expiry:
            return self.__token_expiry
        return None

    @property
    def token_lifespan(self):
        if self.__token_expiry:
            return self.__token_expiry - dt.datetime.utcnow()
        return None

    @property
    def is_logged_in(self):
        if not self.__access_token:
            return False
        return True

    @classmethod
    def parse_key(cls, key=None):
        if not key:
            raise Exception("A key must be provided.")
        return key

    @classmethod
    def parse_secret(cls, secret=None):
        if not secret:
            raise Exception("A secret must be provided.")
        return secret

    # ##################################################################
    # MESSAGE FORMULATION
    # ##################################################################

    def login_message(self):
        msg = message(method=METHOD_LOGIN)
        auth_msg = self.auth_with_credentials(msg)
        return auth_msg

    def logout_message(self):
        msg = message(method=METHOD_LOGOUT)
        return self.auth_with_credentials(msg)

    def auth_with_credentials(self, message):
        if "params" not in message:
            message["params"] = {}
        credentials = {"grant_type": "client_credentials",
                       "client_id": self.key,
                       "client_secret": self.secret}
        message["params"] = {**message["params"], **credentials}
        return message

    def auth_with_access_token(self, messages):

        if not isinstance(messages, list):
            messages = [messages]

        for msg in messages:
            if "params" not in msg:
                msg["params"] = {}
            msg["params"]["access_token"] = self.access_token
        return messages

    # ##################################################################
    # LOGIN INFORMATION PARSING
    # ##################################################################

    def on_deribit_login(self, sender, data=None, websocket=None, **kwargs):
        print("Deribit auth manager received login signal.")
        return self.parse_login_response(response=data)

    def parse_login_response(self, response, **kwargs):

        if RESP_ERROR in response:
            print(response)
            raise Exception("Failed to obtain token from Deribit. Error message received.")

        # Set the tokens
        self.__refresh_token = response[RESP_CONTENT]["refresh_token"]
        self.__access_token = response[RESP_CONTENT]["access_token"]

        # Compute the token expiry datetime
        try:
            lifespan = response[RESP_CONTENT][RESP_CONT_TOK_EXP]
            reference_time = response[RESP_TS_IN]
            expiry_ = dt.timedelta(seconds=lifespan)
            self.__token_expiry = dt.datetime.utcfromtimestamp(reference_time / 1000000) + expiry_
            print(f"Token valid until {self.__token_expiry}")

        except:
            # TODO logging here
            pass

    # ##################################################################
    # WEBSOCKET BASIC OPERATIONS
    # ##################################################################

    @staticmethod
    def on_message(data, **kwargs):
        return data

    async def __async_request(self, messages, auth_required=False, signal=None):

        async def _send_thru_ws(msg, ws):
            await ws.send(json.dumps(msg))
            resp = await ws.recv()
            return json.loads(resp)

        if not signal:
            logging.debug(f"[{self.id}] No signal found. Connecting to default handler.")
            signal = self.on_message

        if not isinstance(messages, list):
            messages = [messages]

        async with websockets.connect(self.__url, max_size=None) as websocket:

            if auth_required or not self.is_logged_in:

                # Authenticate the connection
                log_msg = self.login_message()
                await websocket.send(json.dumps(log_msg))
                login_response = await websocket.recv()

                # Store token if first login
                if not self.is_logged_in:
                    logging.debug(f"[{self.id}] Logging in client.")
                    sig_login.send(data=json.loads(login_response))

            # Authenticate the messages to be sent
            if auth_required:
                messages = [self.auth_with_access_token(messages=msg) for msg in messages]

            _json_msg = [json.dumps(m) for m in messages]
            response = []

            # Gather async tasks and results
            for m in _json_msg:
                await websocket.send(m)
                _ = await websocket.recv()
                response.append(json.loads(_))

            return signal(data=response)

    # ##################################################################
    # SESSION
    # ##################################################################

    async def server_time(self):
        msg = session.get_time()
        return await self.__async_request(messages=msg, auth_required=False)

    async def test(self):
        msg = session.test()
        return await self.__async_request(messages=msg, auth_required=False)

    async def test_exception(self):
        msg = session.test_with_exception()
        return await self.__async_request(messages=msg, auth_required=False)

    # ##################################################################
    # DATA
    # ##################################################################

    async def instruments(self, currency=DEFAULT_CURRENCY, kind=DEFAULT_KIND, expired=False):

        msg = data.request_instruments(currency=currency, kind=kind, expired=expired)

        return await self.__async_request(messages=msg,
                                          auth_required=False,
                                          signal=sig_instrument_received.send)

    async def currencies(self):

        msg = data.request_currencies()

        return await self.__async_request(messages=msg,
                                          auth_required=False,
                                          signal=sig_currency_received.send)

    async def orderbooks(self, instruments, depth=DEFAULT_DEPTH):

        if not isinstance(instruments, list):
            instruments = [instruments]

        msg = data.request_orderbooks(instruments=instruments, depth=depth)

        return await self.__async_request(messages=msg,
                                          auth_required=False,
                                          signal=sig_orderbook_snapshot_received.send)

    # ##################################################################
    # ACCOUNT
    # ##################################################################

    async def position(self, instrument: str):

        msg = account.get_position(instrument=instrument)

        return await self.__async_request(messages=msg,
                                          auth_required=True,
                                          signal=sig_position_received.send)

    async def all_positions(self, currency=DEFAULT_CURRENCY, kind=DEFAULT_KIND):

        msg = account.get_all_positions(currency=currency,
                                        kind=kind)

        return await self.__async_request(messages=msg,
                                          auth_required=True)

    async def account_summary(self, currency=DEFAULT_CURRENCY, extended=True):

        msg = account.get_account_summary(currency=currency,
                                          extended=extended)

        return await self.__async_request(messages=msg,
                                          auth_required=True)

    async def announcements(self):

        msg = account.get_announcements()

        return await self.__async_request(messages=msg,
                                          auth_required=False)

    # ##################################################################
    # TRADING
    # ##################################################################

    async def buy(self,
                  instrument: str,
                  amount: float,
                  order_type: str = None,
                  label: str = None,
                  limit_price: float = None,
                  time_in_force: str = None,
                  max_show: float = None,
                  post_only: bool = False,
                  reduce_only: bool = False,
                  stop_price: float = None,
                  trigger: str = None,
                  vol_quote: bool = False):

        msg = trading.buy(instrument=instrument,
                          amount=amount,
                          order_type=order_type,
                          label=label,
                          limit_price=limit_price,
                          time_in_force=time_in_force,
                          max_show=max_show,
                          post_only=post_only,
                          reduce_only=reduce_only,
                          stop_price=stop_price,
                          trigger=trigger,
                          vol_quote=vol_quote)

        return await self.__async_request(messages=msg,
                                          auth_required=True,
                                          signal=sig_trade_buy_received.send)

    async def sell(self,
                   instrument: str,
                   amount: float,
                   order_type: str = None,
                   label: str = None,
                   limit_price: float = None,
                   time_in_force: str = None,
                   max_show: float = None,
                   post_only: bool = False,
                   reduce_only: bool = False,
                   stop_price: float = None,
                   trigger: str = None,
                   vol_quote: bool = False):

        msg = trading.sell(instrument=instrument,
                           amount=amount,
                           order_type=order_type,
                           label=label,
                           limit_price=limit_price,
                           time_in_force=time_in_force,
                           max_show=max_show,
                           post_only=post_only,
                           reduce_only=reduce_only,
                           stop_price=stop_price,
                           trigger=trigger,
                           vol_quote=vol_quote)

        return await self.__async_request(messages=msg,
                                          auth_required=True,
                                          signal=sig_trade_sell_received.send)

    async def close(self,
                    instrument: str,
                    order_type: str = None,
                    limit_price: float = None):

        msg = trading.close(instrument=instrument,
                            order_type=order_type,
                            limit_price=limit_price)

        return await self.__async_request(messages=msg,
                                          auth_required=True,
                                          signal=sig_trade_close_received.send)

    async def cancel_all(self):

        msg = trading.cancel_all()

        return await self.__async_request(messages=msg,
                                          auth_required=True,
                                          signal=sig_trade_cancel_all_received)

    async def cancel_all_by_currency(self, currency: str, kind: str = None, order_type: str = None):

        msg = trading.cancel_all_by_currency(currency=currency,
                                             kind=kind,
                                             order_type=order_type)

        return await self.__async_request(messages=msg,
                                          auth_required=True,
                                          signal=sig_trade_cancel_received.send)

    async def cancel_all_by_instrument(self, instrument: str, order_type: str = None):

        msg = trading.cancel_all_by_instrument(instrument=instrument,
                                               order_type=order_type)

        return await self.__async_request(messages=msg,
                                          auth_required=True,
                                          signal=sig_trade_cancel_received.send)

    async def estimate_margins(self, instrument: str, amount: float, price: float):

        msg = trading.margins(instrument=instrument,
                              amount=amount,
                              price=price)

        return await self.__async_request(messages=msg,
                                          auth_required=True,
                                          signal=sig_trade_margin_estimate_received.send)

    async def open_orders_by_currency(self, currency: str, kind: str = None, order_type: float = None):

        msg = trading.open_orders_by_currency(currency=currency,
                                              kind=kind,
                                              order_type=order_type)

        return await self.__async_request(messages=msg,
                                          auth_required=True,
                                          signal=sig_trade_open_orders_received.send)

    async def open_orders_by_instrument(self, instrument: str, order_type: float = None):

        msg = trading.open_orders_by_instrument(instrument=instrument,
                                                order_type=order_type)

        return await self.__async_request(messages=msg,
                                          auth_required=True,
                                          signal=sig_trade_open_orders_received.send)

    async def user_trades_by_currency(self, currency: str, kind: str = None,
                                      count: int = None,
                                      include_old: bool = False):

        msg = trading.user_trades_by_currency(currency=currency,
                                              kind=kind,
                                              count=count,
                                              include_old=include_old)

        return await self.__async_request(messages=msg,
                                          auth_required=True,
                                          signal=sig_trade_history_received.send)

    async def user_trades_by_instrument(self, instrument: str, count: int = None, include_old: bool = None):

        msg = trading.user_trades_by_instrument(instrument=instrument,
                                                count=count,
                                                include_old=include_old)

        return await self.__async_request(messages=msg,
                                          auth_required=True,
                                          signal=sig_trade_history_received.send)

    async def order_status(self, order_id: str):

        msg = trading.order_status(order_id=order_id)

        return await self.__async_request(messages=msg,
                                          auth_required=True,
                                          signal=sig_trade_order_status_received.send)


if __name__ == '__main__':

    KEY = "k..."
    SECRET = "s..."

    client = DeribitAsyncClient(key=KEY, secret=SECRET)
    instruments = ["BTC-PERPETUAL" for x in range(500)]

    def on_orderbooks(sender, data):
        print(data)

    sig_orderbook_snapshot_received.connect(on_orderbooks)
    res = client.orderbooks(instruments=instruments, depth=10)

