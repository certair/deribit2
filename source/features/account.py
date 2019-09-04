from source.support.sanitizers import sanitize
from source.features.common import message, add_params_to_message

# ######################################################################
# METHODS
# ######################################################################

METHOD_GET_POSITION = "private/get_position"
METHOD_GET_POSITIONS = "private/get_positions"
METHOD_GET_SUMMARY = "private/get_account_summary"

METHOD_GET_ANNOUNCEMENTS = "public/get_announcements"


# ######################################################################
# POSITIONS
# ######################################################################

def get_position(instrument: str):
    data = sanitize(instrument=instrument)
    msg = message(method=METHOD_GET_POSITION)
    return add_params_to_message({"instrument_name": data["instrument"]}, msg)


def get_all_positions(currency: str = None, kind: str = None):
    data = sanitize(currency=currency, kind=kind)
    msg = message(method=METHOD_GET_POSITIONS)
    params = {"currency": data["currency"], "kind": data["kind"]}
    return add_params_to_message(params, msg)


def get_account_summary(currency: str, extended=True):
    data = sanitize(currency=currency)
    msg = message(method=METHOD_GET_SUMMARY)
    params = {"currency": data["currency"], "extended": extended}
    return add_params_to_message(params, msg)


def get_announcements():
    msg = message(method=METHOD_GET_ANNOUNCEMENTS)
    return add_params_to_message({}, msg)























# The End
