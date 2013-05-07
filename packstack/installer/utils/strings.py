# -*- coding: utf-8 -*-


STR_MASK = '*' * 8
COLORS = {'nocolor': "\033[0m", 'red': "\033[0;31m",
          'green': "\033[92m", 'blue': "\033[94m",
          'yellow': "\033[93m"}


def color_text(text, color):
    """
    Returns given text string with appropriate color tag. Allowed values
    for color parameter are 'red', 'blue', 'green' and 'yellow'.
    """
    return '%s%s%s' % (COLORS[color], text, COLORS['nocolor'])


def mask_string(unmasked, mask_list=None, replace_list=None):
    """
    Replaces words from mask_list with MASK in unmasked string.
    If words are needed to be transformed before masking, transformation
    could be describe in replace list. For example [("'","'\\''")]
    replaces all ' characters with '\\''.
    """
    mask_list = mask_list or []
    replace_list = replace_list or []

    masked = unmasked
    for word in sorted(mask_list, lambda x, y: len(y) - len(x)):
        if not word:
            continue
        for before, after in replace_list:
            word = word.replace(before, after)
        masked = masked.replace(word, STR_MASK)
    return masked
