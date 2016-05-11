# -*- coding: utf-8 -*-
import itertools

def stringify(value):
    if value is None:
        value = ''
    elif type(value) != unicode and type(value) != str:
        value = str(value)
    return value

def get_col_data_by_attr_name(row_item, attr_label):
    cols = [col for col in itertools.chain(row_item['raw'], row_item['eval'], row_item['extend'])
            if col['key'] == attr_label]
    if len(cols) > 0:
        return cols[0]

def correct_col_data_value(col_data, value):
    clear_logger_by_col('validation', col_data)
    col_data['change'] = True
    if 'raw_value' not in col_data:
        col_data['raw_value'] = col_data['value']
    col_data['value'] = value

def log(logger, item, msgs):
    if 'logger' not in item:
        item['logger'] = {}
    if logger not in item['logger']:
        item['logger'][logger] = []
    if msgs and len(msgs) > 0:
        item['logger'][logger].extend(msgs)
    return

def clear_all_logger_by_row(item):
    if 'logger' in item:
        item['logger'] = {}
    for col_item in itertools.chain(item['raw'], item['extend'], item['eval']):
        if 'logger' in col_item:
            col_item['logger'] = {}

def clear_logger_by_row(logger, item):
    if 'logger' in item and logger in item['logger']:
        item['logger'][logger] = []
    for col_item in itertools.chain(item['raw'], item['extend'], item['eval']):
        if 'logger' in col_item and logger in col_item['logger']:
            col_item['logger'][logger] = []

def clear_logger_by_col(logger, item):
    if 'logger' in item and logger in item['logger']:
        item['logger'][logger] = []

def get_logger(logger, item):
    if 'logger' in item and logger in item['logger']:
        return item['logger'][logger]
    return []

def sync_object_by_rows(row_datas):
    for row_data in row_datas:
        row_data['obj'] = {}
        for col_data in itertools.chain(row_data['raw'], row_data['extend'], row_data['eval']):
            key = col_data['key']
            value = col_data['value']
            row_data['obj'][key] = value

