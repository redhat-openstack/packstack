# -*- coding: utf-8 -*-

import time


def retry(count=1, delay=0, retry_on=Exception):
    """
    Decorator which tries to run specified fuction if the previous
    run ended by given exception. Retry count and delays can be also
    specified.
    """
    if count < 0 or delay < 0:
        raise ValueError('Count and delay has to be positive number.')

    def decorator(func):
        def wrapper(*args, **kwargs):
            tried = 0
            while tried <= count:
                try:
                    return func(*args, **kwargs)
                except retry_on:
                    if tried >= count:
                        raise
                    if delay:
                        time.sleep(delay)
                    tried += 1
        wrapper.func_name = func.func_name
        return wrapper
    return decorator
