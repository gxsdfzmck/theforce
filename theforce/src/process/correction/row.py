# -*- coding: utf-8 -*-
from decimal import Decimal
import itertools

import Levenshtein

from util import get_col_data_by_attr_name, correct_col_data_value, get_logger
from numberify import get_possible_int_value, get_possible_float_value

def is_col_data_valid(col_data):
    errors = get_logger('validation', col_data)
    if errors and len(errors)>0:
        return False
    return True


def score_corrector(row_data, args):
    obj = row_data['obj']
    min_data = get_col_data_by_attr_name(row_data, args['min'])
    max_data = get_col_data_by_attr_name(row_data, args['max'])
    mean_data = get_col_data_by_attr_name(row_data, args['mean'])
    count_data = get_col_data_by_attr_name(row_data, args['count'])
    bonus_exprs = args['bonus_expr'] if 'bonus_expr' in args else []

    min_valid = is_col_data_valid(min_data)
    max_valid = is_col_data_valid(max_data)
    mean_valid = is_col_data_valid(mean_data)
    if min_valid and max_valid and mean_valid:
        # 如果OK的就不用检测了
        return

    count_valid = is_col_data_valid(count_data)

    min_datas = []
    max_datas = []
    mean_datas = []
    if min_valid:
        min_datas.append(min_data['value'])
    else:
        min_datas = get_possible_int_value(min_data['value'])
    if max_valid:
        max_datas.append(max_data['value'])
    else:
        max_datas = get_possible_int_value(max_data['value'])
    if mean_valid:
        mean_datas.append(mean_data['value'])
    else:
        mean_datas = get_possible_float_value(mean_data['value'])

    count_value = count_data['value'] if count_valid else -1
    possibles = []
    if len(min_datas) > 0 and len(max_datas) > 0 and len(mean_datas) > 0:
        for min_value, mean_value, max_value in itertools.product(min_datas, mean_datas, max_datas):
            # 智能bonuss方式
            bonus = get_bonus(bonus_exprs, min_value, mean_value, max_value, obj)
                
            min_similarity = cal_similarity(min_data, min_value, min_valid)
            mean_similarity = cal_similarity(mean_data, mean_value, mean_valid)
            max_similarity = cal_similarity(max_data, max_value, max_valid)
            similarity = sum([min_similarity, mean_similarity, max_similarity])/3
            possible_score = score(min_value, mean_value, max_value, count_value, similarity)

            if possible_score > 0:
                possibles.append({'min': min_value, 'max': max_value, 'mean': mean_value, 'score': possible_score + bonus})

    values = None
    if len(possibles) == 1:
        # 正好一个
        values = possibles[0]
    elif len(possibles) > 1:
        # 多于一个时，选择最高的值的那个，并且在控制台列出其他可选值
        order_values = sorted(possibles, key=lambda item: -item['score'])
        if len(order_values) == 1:
            values = order_values[0]
        else:
            first_values = order_values[0]
            second_values = order_values[1]
            if first_values['score'] == second_values['score']:
                print u'太过相似，无法判断选择。'
                print order_values
            else:
                values = first_values
                if first_values['score'] - second_values['score'] < 5:
                    print u'请注意以下替换，较相似，已选用首选值。'
                    print order_values
    if values is not None:
        print 'Row Correct:', values
        if not min_valid:
            correct_col_data_value(min_data, values['min'])
        if not mean_valid:
            correct_col_data_value(mean_data, values['mean'])
        if not max_valid:
            correct_col_data_value(max_data, values['max'])

def get_bonus(bonus_exprs, min_value, mean_value, max_value, obj):
    bonus = 0
    for bonus_expr in bonus_exprs:
        try:
            if eval(bonus_expr['expr']):
                bonus += int(bonus_expr['bonus'])
        except Exception, e:
            pass
    return bonus

def cal_similarity(data, value, valid):
    if valid:
        return 1
    else:
        if type(data['value']) == unicode or type(value)==unicode:
            init = unicode(data['value'])
            value = unicode(value)
        else:
            init = str(data['value'])
            value = str(value)
        return Levenshtein.ratio(init, value)
        
    
def score(min_value, mean_value, max_value, count_value, similarity):
    if min_value <= mean_value and mean_value<=max_value:
        # 符合基本条件
        if count_value == 1:
            if min_value == mean_value and mean_value == max_value:
                return 100
            else:
                return 0
        elif count_value == 2:
            if (min_value+max_value) == mean_value*2:
                return 100
            else:
                return 0
        return 99*similarity
    return 0


