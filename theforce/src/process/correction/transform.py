# -*- coding: utf-8 -*-

DOT_LIKE_CHARS = [',', '.', ':', '\'', '"', ' ', u'‘', u'’', u'，', u'。', u'：',
                  u'“', u'”']
DOT_LIKE_CHARS2 = ''.join(DOT_LIKE_CHARS)

def trim_dot_like(input):
    if input is None:
        return None
    if type(input) is str or type(input) is unicode:
        for char in DOT_LIKE_CHARS:
            input = input.replace(char, '')
    return input


def ltrim_dot_like(input):
    if input is None:
        return None
    if type(input) is str or type(input) is unicode:
        return input.lstrip(DOT_LIKE_CHARS2)
    return input


def rtrim_dot_like(input):
    if input is None:
        return None
    if type(input) is str or type(input) is unicode:
        return input.rstrip(DOT_LIKE_CHARS2)
    return input
