from blinker import signal

# ##################################################################
# LOGIN / LOGOUT
# ##################################################################

sig_login = signal("DERIBIT-LOGIN")


# ##################################################################
# MARKET DATA
# ##################################################################

sig_instrument_received = signal("DERIBIT-INSTRUMENTS-RECEIVED")
sig_index_level_received = signal("DERIBIT-INDEX-LEVEL-RECEIVED")
sig_currency_received = signal("DERIBIT-CURRENCY-RECEIVED")
sig_orderbook_snapshot_received = signal("DERIBIT-ORDERBOOK-SNAPSHOT-RECEIVED")


# ##################################################################
# ACCOUNT
# ##################################################################

sig_position_received = signal("DERIBIT-ACCOUNT-POSITION-RECEIVED")
sig_all_positions_received = signal("DERIBIT-ACCOUNT-POSITIONS-RECEIVED")
sig_account_summary = signal("DERIBIT-ACCOUNT-SUMMARY-RECEIVED")
sig_announcement = signal("DERIBIT-ACCOUNT-ANNOUNCEMENT-RECEIVED")


# ##################################################################
# TRADING
# ##################################################################

sig_trade_buy_received = signal("DERIBIT-TRADE-BUY-RECEIVED")
sig_trade_sell_received = signal("DERIBIT-TRADE-SELL-RECEIVED")
sig_trade_close_received = signal("DERIBIT-TRADE-CLOSE-RECEIVED")
sig_trade_cancel_received = signal("DERIBIT-TRADE-CANCEL-RECEIVED")
sig_trade_cancel_all_received = signal("DERIBIT-TRADE-CANCEL-ALL-RECEIVED")

sig_trade_margin_estimate_received = signal("DERIBIT-TRADE-MARGIN-ESTIMATE-RECEIVED")

sig_trade_open_orders_received = signal("DERIBIT-TRADE-OPEN-ORDERS-RECEIVED")
sig_trade_history_received = signal("DERIBIT-TRADE-HISTORY-RECEIVED")

sig_trade_order_status_received = signal("DERIBIT-TRADE-ORDER-STATUS-RECEIVED")






# The End
