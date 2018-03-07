# -*- coding: utf-8 -*-
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
        wrapper.__name__ = func.__name__
        return wrapper
    return decorator
