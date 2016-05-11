# -*- coding: utf-8 -*-
import itertools

from validation import validation
from correction import correction
from evaluation import evaluation
from util import clear_logger_by_row, log, get_col_data_by_attr_name, stringify

def exec_validation(name, col_value, _validation):
    errors = []
    if _validation:
        for rule_str in _validation:
            value = col_value['value'] if col_value else None
            if not validation.validate(rule_str, value):
                error = u'[V]属性({0})验证规则({1})失败:{2}'.format(name, rule_str,
                                                            value)
                errors.append(error)
    return errors

def exec_group_validation(row_datas, validations):
    for row_data in row_datas:
        clear_logger_by_row('order', row_data)
        clear_logger_by_row('duplicate', row_data)
        clear_logger_by_row('continuous_unique', row_data)

    errors = []
    if validations and len(validations)>0:
        for _validation in validations:
            rule_name = _validation['rule']
            params = _validation['params']
            try:
                errors.extend(validation.group_validate(rule_name, params, row_datas))
            except Exception,e:
                continue
    return errors

def exec_sample_validation(row_datas, samples):
    errors = []
    for sample in samples:
        fields = sample['type'].strip().split(',')
        for sample_data in sample['datas']:
            is_found = False
            for row_data in row_datas:
                if is_found:
                    break
                values = []

                for attr_label in fields:
                    col_data = get_col_data_by_attr_name(row_data, attr_label)
                    values.append(stringify(col_data['value']).strip() if col_data and 'value' in col_data else '')

                if ','.join(values) == sample_data.strip():
                    is_found = True
            if not is_found:
                errors.append(u'未找到({}):{}'.format(sample['type'], sample_data))
    return errors


def count_key_lambda(fields):
    def count_key(row_data):
        values = []
        for attr_label in fields:
            col_data = get_col_data_by_attr_name(row_data, attr_label)
            values.append(stringify(col_data['value']).strip() if col_data and 'value' in col_data else '')
        return ','.join(values)
    return count_key

def exec_count_validation(row_datas, count_metas):
    errors = []
    if count_metas:
        for count_meta in count_metas:
            meta = count_meta['type'].strip()
            metas = meta.split('#')
            if len(metas) == 1:
                metas.append('')
            meta_datas = count_meta['datas']

            key_fields = metas[0].split(',')
            count_fields = metas[1].split(',')

            key_fn = count_key_lambda(key_fields)
            sorted_datas = sorted(row_datas, key=key_fn)

            counters = {}
            for group, group_items in itertools.groupby(sorted_datas, key=key_fn):
                if len(count_fields) == 1 and count_fields[0] == '':
                    count = len(list(group_items))
                else:
                    count_fn = count_key_lambda(count_fields)
                    group_datas = sorted(list(group_items), key=count_fn)
                    count = len(list(itertools.groupby(group_datas, key=count_fn)))

                counters[group] = count

            for key, value in meta_datas.items():
                key = str(key)
                if key not in counters:
                    if int(value) != 0:
                        errors.append(u'类型{} - {}: 未找到'.format(meta, key))
                elif counters[key] != int(value):
                    errors.append(u'类型{} - {}: {}(期望) - {}(实际)'.format(meta, key, value, counters[key]))
    return errors

def exec_row_validation(row_datas, validations):
    for row_data in row_datas:
        clear_logger_by_row('validation_row', row_data)
    errors = []
    if validations and len(validations)>0:
        for _validation in validations:
            name = _validation['name']
            expr = _validation['expr']
            when = _validation['when'] if 'when' in _validation else 'True'
            for row_data in row_datas:
                result = validation.validate_row(expr, when, row_data)
                if not result:
                    msg = u'行级校验错误：{0}'.format(name)
                    log('validation_row', row_data, [msg])
                    errors.append(msg)
    return errors

def exec_row_correction(row_datas, corrections):
    errors = []
    if corrections:
        for _correction in corrections:
            for row_data in row_datas:
                try:
                    # 尝试fixed
                    correction.correct_row(_correction['type'], row_data, _correction['args'])
                except Exception, e:
                    error = u'发生错误: {0}'.format(e)
                    print error
                    errors.append(error)
    return errors



def exec_correction(name, value, _correction):
    errors = []
    warnings = []
    last_value = value
    if _correction:
        for correction_str in _correction:
            try:
                value = correction.correct(correction_str, last_value)
            except Exception, e:
                error = u'[C]修正属性({0})(规则:{1})时失败[{2}]:{3}'.format(
                    name, correction_str, last_value, e.message)
                errors.append(error)
                break

            if value != last_value:
                warning = u'[C]规则{0}修改属性{1}值: {2} -> {3}'.format(
                    correction_str, name, last_value, value)
                warnings.append(warning)
            last_value = value

    return errors, warnings, value


def exec_evaluation(context, attr_label, formulas):
    warnings = []
    value = None
    if formulas:
        for formula in formulas:
            if value is not None:
                break
            eval_type = formula['type']
            eval_param = formula['param']
            try:
                value = evaluation.evaluate(eval_type, eval_param, context)
            except Exception, e:
                msg = u'[E]公式{0}-{1}计算值{2}失败.'.format(eval_type, eval_param,
                                                      attr_label)
                warnings.append(msg)
    return [], warnings, value
