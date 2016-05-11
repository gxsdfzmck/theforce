import itertools

from util import get_col_data_by_attr_name

def clear_log_by_row(msg_type, msg_level, item):
    if 'missing' in item:
        item['missing'] = [ _item for _item in item['missing'] if _item['msg_type'] != msg_type and _item['msg_level']!= msg_level]
    key = '_' + msg_type
    for col_item in itertools.chain(item['raw'], item['eval']):
        col_item[key] = []

def log_col_by_row(msg_type, msg_level, item, attr, msgs):
    col_data = get_col_data_by_attr_name(item, attr)
    if col_data:
        log_col(msg_type, msg_level, col_data, msgs)
    else:
        item['missing'].append({'msg_type': msg_type,
                                'msg_level': msg_level,
                                'key': attr,
                                'msgs': msgs})


def log_col(msg_type, msg_level, col_item, msgs):
    key = "_" + msg_type
    if key not in col_item:
        col_item[key] = []

    if msgs and len(msgs) > 0:
        col_item[key].extend(msgs)
    return


