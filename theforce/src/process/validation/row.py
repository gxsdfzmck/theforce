# -*- coding: utf-8 -*-

def eval_rule(obj, params):
    expr = params['expr']
    when = params['when']

    try:
        when_value = eval(when) if when else True
        if when_value:
            return eval(expr)
    except Exception,e:
        print e
        return False
    return True
