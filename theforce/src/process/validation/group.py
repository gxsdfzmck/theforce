# -*- coding: utf-8 -*-
from decimal import Decimal
import itertools
from util import stringify, get_col_data_by_attr_name, log, correct_col_data_value

def decimalify(input):
    try:
        return Decimal(input)
    except:
        pass

def order(row_datas, params):
    group_keys = params['group']
    orders = params['order']
    is_fix = params['fix'] if 'fix' in params else True
    
    order_items = orders.split(';')
    order_keys = [_item.split(',')[0] for _item in order_items]
    order_types = [_item.split(',')[1] for _item in order_items]
    errors = []

    def group_fn(row_data):
        key = '|'.join([stringify(item['value']) for item in row_data['raw'] if item['key'] in group_keys])
        return key
        
    for group_name, group_datas in itertools.groupby(row_datas, group_fn):
        order_caches = [None]*len(order_keys)
        group_datas = [_item for _item in group_datas]

        # 先纠错
        if is_fix:
            for data_index, row_data in enumerate(group_datas):
                pre_row_data = group_datas[data_index-1] if data_index > 0 else None
                next_row_data = group_datas[data_index+1] if (data_index+1)<len(group_datas) else None
                if pre_row_data and next_row_data:
                    for index, order_key in enumerate(order_keys):
                        col_data = get_col_data_by_attr_name(row_data, order_key)
                        pre_data = get_col_data_by_attr_name(pre_row_data, order_key)
                        next_data = get_col_data_by_attr_name(next_row_data, order_key)
                        if col_data and pre_data and next_data:
                            order_type = order_types[index].upper()
                            diff_value = 2 if order_type == 'ASC' else -2
                            add_value = 1 if order_type == 'ASC' else -1
                            try:
                                if decimalify(next_data['value']) - decimalify(pre_data['value']) == diff_value:
                                    new_value = decimalify(pre_data['value']) + add_value
                                    if new_value != decimalify(col_data['value']):
                                        new_label = new_value
                                        if type(pre_data['value']) == str or type(pre_data['value']) == unicode:
                                            len_me = len(str(new_label))
                                            len_pre = len(pre_data['value'].strip())
                                            if len_me < len_pre:
                                                new_label = '0'*(len_pre - len_me) + str(new_label)
                                        print u'自动修复了数据序号，行号：{0} 修改为 {1}->{2}'.format(col_data['row'], col_data['value'], new_label)
                                        correct_col_data_value(col_data, new_label)
                            except Exception, e:
                                pass

        # 再校验
        for row_data in group_datas:
            for index, order_key in enumerate(order_keys):
                col_data = get_col_data_by_attr_name(row_data, order_key)
                if col_data is None:
                    continue

                col_value = decimalify(col_data['value'])

                order_type = order_types[index]
                if order_caches[index] is None:
                    order_caches[index] = col_value
                elif col_value is None:
                    continue
                else:
                    # 比较
                    if order_type.upper() == 'ASC' and order_caches[index] >= col_value:
                        msg = u'升序较验错误：{0}，当前值为{1},上一条非空值为{2}'.format(order_key, col_value, order_caches[index])
                        errors.append(msg)
                        log('order', col_data, [msg])
                    elif order_type.upper() == 'DESC' and order_caches[index] <= col_value:
                        msg = u'降序较验错误：{0}，当前值为{1},上一条非空值为{2}'.format(order_key, col_value, order_caches[index])
                        errors.append(msg)
                        log('order', col_data, [msg])
                    order_caches[index] = col_value
    return errors
                        
def duplicate(row_datas, duplicate_keys=[]):
    errors = []
    def group_fn(row_data):
        return '|'.join([stringify(item['value']).strip() for item in row_data['raw'] if item['key'] in duplicate_keys])

    row_datas = sorted(row_datas, key=group_fn)
    for group_name, group_datas in itertools.groupby(row_datas, group_fn):
        group_datas = [_item for _item in group_datas]
        if len(group_datas)>1:
            # 处理重复数据
            msg_data = ';'.join(['{0}'.format(_row['row']) for _row in group_datas])
            msg = u'以下数据可能存在重复数据，请查阅以下行:{0}'.format(msg_data)
            errors.append(msg)
            for row_data in group_datas:

                log('duplicate', row_data, [msg])

    return errors
        
def continuous_unique(row_datas, params):
    errors = []

    name = params['name']
    fields = params['fields']
    fields_label = ','.join(fields)

    histories = {}
    last_key = None
    for row_data in row_datas:
        col_values = []
        for field in fields:
            col_data = get_col_data_by_attr_name(row_data, order_key)
            col_values.append(col_data['value'] if col_data else '')
        key = '##'.join(col_values)
        if last_key != key:
            last_key = key
            if key not in histories:
                histories[key] = row_data['row']
            else:
                # 此行数据有问题
                msg = u'{}: 当前值 [{}] 被间断，第一次出现在第 {} 行'.format(name, fields_label, histories[key])
                errors.append(msg)
                log('continuous_unique', row_data, [msg])
    return errors
            
        




                        


            


    
