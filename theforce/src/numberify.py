# -*- coding: utf-8 -*-
import itertools

NUMBER_CHARS = '0123456789.'

REPLACE_CHARS = {
    'B': ['3', '8'],
    'S': ['8', '5'],
    'J': ['1'],
    'L': ['1.', ''],
    'H': ['11'],
    'Z': ['2'],
    '/': ['.'],
    'Q': ['0'],
    'U': ['0', '0.', '1.']
}


def get_possible_inputs(input):
    max_length = len(input)
    inputs = []
    for length in range(1, max_length+1):
        for indexes in itertools.combinations(range(0, max_length), length):
            inputs.append(''.join(
                [char for i, char in enumerate(input) if i in indexes]))
    return inputs


def clean_int_value(input):
    if type(input) is str or type(input) is unicode:
        chars = []
        chars.append([' ', ''])
        chars.append(['o', '0'])
        chars.append(['O', '0'])
        chars.append(['I', '1'])
        chars.append(['l', '1'])
        chars.append(['!', '1'])
        chars.append([']', '1'])
        chars.append([u'】', '1'])
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


def parse_int(input):
    try:
        return int(input)
    except:
        return None


def append_int(values, input):
    input_int = parse_int(input)
    if input_int is not None:
        if input_int not in values:
            values.append(input_int)
        return True
    return False


def get_possible_int_value(input, max_int=750):
    if type(input) != str and type(input) != unicode:
        input = str(input)
    input = clean_int_value(input)

    inputs = []
    raw_int = parse_int(input)
    if raw_int is None:
        # 有特殊字符 & 替换字典中的可能值
        possibles = [input]
        for _char, _replacements in REPLACE_CHARS.items():
            possibles = set([_item.replace(_char, _replacement)
                             for _replacement in _replacements for _item in
                             possibles])
        inputs.extend(possibles)
    else:
        inputs.append(input)

    all_possible_inputs = []
    for _input in inputs:
        all_possible_inputs.extend(get_possible_inputs(_input))

    values = []
    for _input in all_possible_inputs:
        append_int(values, _input)

    if max_int is not None:
        values = [value for value in values if value <= max_int]
    return set(values)


def clean_float_value(input):
    if type(input) is str or type(input) is unicode:
        chars = []
        chars.append([' ', ''])
        chars.append(['o', '0'])
        chars.append(['O', '0'])
        chars.append(['I', '1'])
        chars.append(['l', '1'])
        chars.append(['!', '1'])
        chars.append([']', '1'])
        chars.append([u'】', '1'])
        chars.append(['.', '.'])
        chars.append([u'。', '.'])
        chars.append([':', '.'])
        chars.append([';', '.'])
        chars.append([',', '.'])
        chars.append([u'，', '.'])
        chars.append([u'：', '.'])
        for group in chars:
            input = input.replace(group[0], group[1])
    return input


def parse_float(input):
    try:
        try:
            return int(input)
        except:
            return float(input)
    except:
        return None


def append_float(values, input):
    input_float = parse_float(input)
    if input_float is not None:
        if input_float not in values:
            values.append(input_float)
        return True
    return False


def get_possible_float_value(input, max_float=750):
    if type(input) != str and type(input) != unicode:
        input = str(input)
    input = clean_float_value(input)

    inputs = []
    raw_float = parse_float(input)
    if raw_float is None:
        # 有特殊字符 & 替换字典中的可能值
        possibles = [input]
        for _char, _replacements in REPLACE_CHARS.items():
            possibles = set([_item.replace(_char, _replacement)
                             for _replacement in _replacements for _item in
                             possibles])
        inputs.extend(possibles)
    else:
        inputs.append(input)

    all_possible_inputs = []
    for _input in inputs:
        all_possible_inputs.extend(get_possible_inputs(_input))

    values = []
    for _input in all_possible_inputs:
        append_float(values, _input)

    dotted_values = []
    for float_value in values:
        dotted_values.extend(get_dotted_float(float_value))
    values.extend(dotted_values)

    if max_float is not None:
        values = [value for value in values if value <= max_float]
    return set(values)

def get_dotted_float(float_value):
    str_value = str(float_value)
    values = []
    if str_value.find('.')<0:
        for i in range(1, len(str_value)):
            try:
                values.append(float(str_value[0:i]+'.'+str_value[i:]))
            except:
                continue
    return values
        
