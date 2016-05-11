# -*- coding: utf-8 -*-
import basetype
import custom
import transform
import row

class Correction:

    def __init__(self):
        self.corrections = {}

    def add(self, name, function):
        self.corrections[name] = function

    def list(self):
        return self.corrections.keys()

    def correct(self, type_str, value):
        if type_str not in self.corrections:
            raise Exception(u'找不到类型规则:%s.' % (type_str))
        else:
            return self.corrections[type_str](value)

    def correct_row(self, type_str, row_value, args):
        if type_str not in self.corrections:
            raise Exception(u'找不到类型规则:%s.' % (type_str))
        else:
            return self.corrections[type_str](row_value, args)


correction = Correction()
correction.add('trim_dot_like', transform.trim_dot_like)
correction.add('ltrim_dot_like', transform.ltrim_dot_like)
correction.add('rtrim_dot_like', transform.rtrim_dot_like)
correction.add('int', basetype.int_type)
correction.add('int2', basetype.int2_type)
correction.add('float2', basetype.float2_type)
correction.add('subject_name', custom.subject_name)
correction.add('year', custom.year)
correction.add('score', row.score_corrector)
