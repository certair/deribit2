import asyncio
import logging
import random
import string


# ######################################################################
# ENDPOINTS
# ######################################################################

def grab_event_loop(loop=None):
    if not loop:
        return __grab_new_event_loop()

    if loop.is_closed():
        return __grab_new_event_loop()

    elif not loop.is_running():
        __close_event_loop(loop=loop)
        return __grab_new_event_loop()

    while loop.is_running():
        asyncio.wait(loop=loop, fs=asyncio.Task.all_tasks())
    if not loop.is_closed():
        __close_event_loop(loop=loop)
    return __grab_new_event_loop()


def __close_event_loop(loop):
    try:
        loop.close()
    except:
        logging.warning("Trying to close existing event loop failed.")


def __grab_new_event_loop():
    try:
        return asyncio.new_event_loop()
    except:
        raise Exception("Unable to create an event loop.")


# ######################################################################
# ENDPOINTS
# ######################################################################

def generate_id(letters=3, numbers=7):
    begin = generate_random_letters(letters)
    end = generate_random_numbers(numbers)
    return begin + end


def generate_random_letters(length):
    return ''.join(random.SystemRandom().choice(string.ascii_uppercase) for _ in range(length))


def generate_random_numbers(length):
    id_ = ''.join(random.SystemRandom().choice(string.digits) for _ in range(length))
    if id_[0] == '0':
        return generate_random_numbers(length=length)
    return id_


def generate_random_characters(length):
    id_ = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(length))
    if id_[0] == '0':
        return generate_random_numbers(length=length)
    return id_
