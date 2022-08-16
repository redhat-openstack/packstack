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

from functools import cmp_to_key
import re


STR_MASK = '*' * 8
COLORS = {'nocolor': "\033[0m", 'red': "\033[0;31m",
          'green': "\033[32m", 'blue': "\033[34m",
          'yellow': "\033[33m"}


def color_text(text, color):
    """
    Returns given text string with appropriate color tag. Allowed values
    for color parameter are 'red', 'blue', 'green' and 'yellow'.
    """
    return '%s%s%s' % (COLORS[color], text, COLORS['nocolor'])


def stringcmp(x, y):
    return len(y) - len(x)


def mask_string(unmasked, mask_list=None, replace_list=None):
    """
    Replaces words from mask_list with MASK in unmasked string.
    If words are needed to be transformed before masking, transformation
    could be describe in replace list. For example [("'","'\\''")]
    replaces all ' characters with '\\''.
    """
    mask_list = mask_list or []
    replace_list = replace_list or []

    if isinstance(unmasked, str):
        masked = unmasked.encode('utf-8')
    else:
        masked = unmasked

    for word in sorted(mask_list, key=cmp_to_key(stringcmp)):
        if not word:
            continue
        word = word.encode('utf-8')
        for before, after in replace_list:
            word = word.replace(before.encode('utf-8'), after.encode('utf-8'))
        masked = masked.replace(word, STR_MASK.encode('utf-8'))
    return masked.decode('utf-8')


def state_format(msg, state, color):
    """
    Formats state with offset according to given message.
    """
    _msg = '%s' % msg.strip()
    for clr in COLORS.values():
        _msg = re.sub(re.escape(clr), '', msg)

    space = 70 - len(_msg)
    state = '[ %s ]' % color_text(state, color)
    return state.rjust(space)


def state_message(msg, state, color):
    """
    Formats given message with colored state information.
    """
    return '%s%s' % (msg, state_format(msg, state, color))
