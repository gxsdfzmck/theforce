# -*- coding: utf-8 -*-
def require_param(param):
    if not param or len(param) is 0:
        raise Exception(u'规则没有传入额外的参数值')


def is_int(value):
    try:
        int(value)
    except:
        return False
    else:
        return True


def ignore_empty_input(func):
    """
    如果是空值则忽略，并返回True
    """

    def __decorator(input, param):
        if not required_rule(input):
            return True
        else:
            return func(input, param)

    return __decorator


def required_rule(input, param=''):
    if input is not None:
        if input.__class__ is str:
            return len(input.strip()) > 0
        else:
            return True
    return False


@ignore_empty_input
def min_rule(input, param=''):
    require_param(param)
    if input:
        if is_int(param):
            return input > int(param)
        else:
            raise Exception(u'min规则传入的参数非法: %s' % param)
    else:
        return True


@ignore_empty_input
def max_rule(input, param=''):
    require_param(param)
    if is_int(param):
        return input < int(param)
    else:
        raise Exception(u'max规则传入的参数非法: %s' % param)


@ignore_empty_input
def enum_rule(input, param=''):
    require_param(param)
    values = param.split('|')
    try:
        values.index(input)
    except:
        return False
    else:
        return True
