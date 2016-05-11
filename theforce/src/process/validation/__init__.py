# -*- coding: utf-8 -*-
import rules
import group
import row


class Validation:
    def __init__(self):
        self.validations = {}

    def add(self, name, function):
        self.validations[name] = function

    def list(self):
        return self.validations.keys()

    def validate(self, rule_str, value):
        """
        列级校验
        """
        rule_param = ''
        rule_name = rule_str
        if rule_str.find(':') > 0:
            sep_index = rule_str.index(':')
            rule_param = rule_str[sep_index + 1:]
            rule_name = rule_str[0:sep_index]
        if rule_name not in self.validations:
            raise Exception(u'找不到校验规则:%s。(%s)' % (rule_name, rule_str))
        else:
            return self.validations[rule_name](value, rule_param)

    def group_validate(self, rule_name, rule_params, row_datas):
        """
        组级校验
        """
        if rule_name not in self.validations:
            raise Exception(u'找不到校验规则:%s。' % (rule_name))
        else:
            return self.validations[rule_name](row_datas, rule_params)

    def validate_row(self, expr, when, row_data):
        """
        行级校验
        """
        validator = self.validations['row_eval']
        return validator(obj=row_data['obj'], params={'expr': expr, 'when': when})


validation = Validation()
validation.add('required', rules.required_rule)
validation.add('enum', rules.enum_rule)
validation.add('min', rules.min_rule)
validation.add('max', rules.max_rule)
validation.add('order', group.order)
validation.add('duplicate', group.duplicate)
validation.add('continuous_unique', group.continuous_unique)
validation.add('row_eval', row.eval_rule)
