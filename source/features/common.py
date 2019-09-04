from typing import List

from source.utilities import generate_id
from source.support.networking import *


# ######################################################################
# PUBLIC
# ######################################################################

@property
def empty_message():
    return message()


def message(method=None, msg=None):

    if not msg:
        msg = add_message_id(message=add_rpc_protocol({}))

    if not method:
        return msg

    return add_method(method, msg)


def add_method(method, message=None):
    message[REQ_METHOD] = method
    return message


def add_params_to_message(kvp_dict, message):
    if REQ_PARAMS not in message:
        message[REQ_PARAMS] = {}
    for k in kvp_dict:
        if kvp_dict[k]:
            message[REQ_PARAMS][k] = kvp_dict[k]
    return message


def add_channels_to_message(channels: List, message):
    if not isinstance(channels, List):
        channels = [channels]
    if REQ_PARAMS not in message:
        message[REQ_PARAMS] = {}
    channels[REQ_PARAMS][CHANNELS] = channels
    return channels


# ##################################################################
# PRIVATE METHODS
# ##################################################################

def generate_message_id():
    return generate_id()


def add_rpc_protocol(message):
    message[PROTOCOL] = PROTOCOL_VERSION
    return message


def add_message_id(message, id=None):
    id_ = id
    if not id_:
        id_ = generate_message_id()
    message["id"] = id_
    return message






















































# The End
