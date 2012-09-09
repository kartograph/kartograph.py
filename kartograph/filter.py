
"""
layer filter
"""

import re


def filter_record(filt, record):
    if isinstance(filt, dict):
        if 'and' in filt:
            res = True
            for sfilt in filt['and']:
                res = res and filter_record(sfilt, record)
        elif 'or' in filt:
            res = False
            for sfilt in filt['or']:
                res = res or filter_record(sfilt, record)
        else:
            res = True
            for key in filt:
                if isinstance(filt[key], (list, tuple)):
                    res = res and filter_record([key, 'in', filt[key]], record)
                else:
                    res = res and filter_record([key, '=', filt[key]], record)
    elif isinstance(filt, (list, tuple)):
        res = filter_single(filt, record)
    elif hasattr(filt, '__call__'):
        res = filt(record)
    return res


def filter_single(filt, record):
    key, comp, val = filt
    prop = record[key]
    comp = comp.lower().split(' ')

    if 'in' in comp:
        res = prop in val
    elif 'like' in comp:
        res = re.search('^' + _escape_regex(val).replace('%', '.*') + '$', prop) is not None
    elif 'matches' in comp:
        res = re.search(val, prop) is not None
    elif 'is' in comp or '=' in comp:
        res = prop == val
    elif 'greater' in comp or ('>' in comp):
        res = prop > val
    elif 'less' in comp or '<' in comp:
        res = prop < val
    if 'not' in comp:
        return not res
    else:
        return res


def _escape_regex(s):
    chars = ('.', '*', '?', '+', '(', ')', '[', ']', '-')
    for c in chars:
        s = s.replace(c, '\\' + c)
    return s
