from typing import List
from source.features.common import message, add_params_to_message


# ######################################################################
# METHODS (ENDPOINTS)
# ######################################################################

METHOD_SUBSCRIBE = "public/subscribe"

METHOD_GET_TIME = "public/get_time"
METHOD_TEST = "public/test"

METHOD_SET_HEARTBEAT = "public/set_heartbeat"
METHOD_DISABLE_HEARTBEAT = "public/disable_heartbeat"

METHOD_ENABLE_CANCEL_ON_DISCONNECT = "private/enable_cancel_on_disconnect"
METHOD_DISABLE_CANCEL_ON_DISCONNECT = "private/disable_cancel_on_disconnect"


# ######################################################################
# ACCOUNT MANAGEMENT FUNCTIONS
# ######################################################################

def set_heartbeat_message():
    msg = message(method=METHOD_SET_HEARTBEAT)
    return add_params_to_message(kvp_dict={"interval": 30}, message=msg)


def disable_heartbeat_message():
    msg = message(method=METHOD_SET_HEARTBEAT)
    return add_params_to_message(kvp_dict={}, message=msg)


def get_time():
    msg = message(method=METHOD_GET_TIME)
    return add_params_to_message(kvp_dict={}, message=msg)


def test():
    msg = message(method=METHOD_TEST)
    return add_params_to_message(kvp_dict={}, message=msg)


def test_with_exception():
    msg = message(method=METHOD_TEST)
    return add_params_to_message(kvp_dict={"expected_result" : "exception"}, message=msg)


def subscription_message(channels):

    if not isinstance(channels, List):
        channels = [channels]

    msg = message(method=METHOD_SUBSCRIBE)
    params = {"channels": channels}
    return add_params_to_message(params, msg)




















# The End