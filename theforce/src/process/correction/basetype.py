# -*- coding: utf-8 -*-


def int_type(input):
    if input is None:
        return None
    try:
        return int(input)
    except:
        raise Exception(u'{0}无法解析成int类型'.format(input))

def int_replace(input):
    chars = []
    chars.append([' ', ''])
    chars.append(['o', '0'])
    chars.append(['O', '0'])
    chars.append(['I', '1'])
    chars.append(['l', '1'])
    chars.append(['!', '1'])
    chars.append([']', '1'])
    chars.append(['.', ''])
    chars.append([u'。', ''])
    chars.append([':', ''])
    chars.append([';', ''])
    chars.append([',', ''])
    chars.append([u'，', ''])
    chars.append([u'：', ''])
    for group in chars:
        input = input.replace(group[0], group[1])
    return input


def float_replace(input):
    chars = []
    chars.append([' ', ''])
    chars.append(['o', '0'])
    chars.append(['O', '0'])
    chars.append(['I', '1'])
    chars.append(['l', '1'])
    chars.append([']', '1'])
    chars.append(['!', '1'])
    chars.append([':', '.'])
    chars.append([';', '.'])
    chars.append([',', '.'])
    chars.append([u'，', '.'])
    chars.append([u'：', '.'])
    chars.append(['..', '.'])
    for group in chars:
        input = input.replace(group[0], group[1])
    return input

def int2_type(input):
    """
    更聪明的int类型.

    1. 消除由ocr引起的.字符
    2. 把0识别成o/O的问题
    """
    if input is None:
        return None
    try:
        if input.__class__ != str and type(input) != unicode:
            input = str(input)
        input = int_replace(input)
        return int(input)
    except:
        raise Exception(u'{0}无法解析成int类型'.format(input))

def float2_type(input):
    if input is None:
        return None
    try:
        if type(input) != str and type(input) != unicode:
            input = str(input)
        input = float_replace(input)
        if input.endswith('.'):
            input = input[:-1]
        try:
            return int(input)
        except Exception:
            pass
        return float(input)
    except:
        raise Exception(u'{0}无法解析成float类型'.format(input))

