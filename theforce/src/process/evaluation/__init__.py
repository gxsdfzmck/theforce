# -*- coding: utf-8 -*-
import re

class Evaluation:

    def __init__(self):
        self.evaluations = {}

    def add(self, name, function):
        self.evaluations[name] = function

    def list(self):
        return self.evaluations.keys()

    def evaluate(self, eval_type, eval_param, obj):
        if eval_type not in self.evaluations:
            raise Exception(u'找不到计算规则:%s。' % eval_type)
        else:
            return self.evaluations[eval_type](obj, eval_param)

evaluation = Evaluation()

evaluation.add('eval', lambda obj, expr: eval(expr))

