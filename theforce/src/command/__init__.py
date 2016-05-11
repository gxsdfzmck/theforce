# -*- coding: utf-8 -*-
import sys
import os.path
import config
import itertools
import operator

import yaml
import MySQLdb
from openpyxl import load_workbook
from pymongo.mongo_client import MongoClient

from model import get_attrs, get_collection
from logger import echo_header

from .load import ExcelLoader
from .extension import compute_unit
from .validation import validate_unit
from .corrector import correct_unit
from .save2excel import save
#from .save2mysql import save2mysql
from process import exec_group_validation, exec_row_validation, exec_row_correction, exec_sample_validation, exec_count_validation
from util import stringify, clear_logger_by_row, clear_logger_by_col, get_logger, correct_col_data_value


class Commander(object):
    def __init__(self, paths):
        self._path = paths
        self._data = self.scan_for_data(paths)
        self._summary = {
            'error': [],
            'warning': [],
            'error-obj': [],
            'obj': []
        }
        self._raw = []

    @staticmethod
    def detect_data(config_abs_path, is_parse=True):
        if config_abs_path.endswith('.yml'):
            excel_abs_path = u"{0}.xlsx".format(config_abs_path[:-4])
            if os.path.isfile(excel_abs_path) and os.path.isfile(
                    config_abs_path):
                if is_parse:
                    with open(config_abs_path) as f:
                        excel_config = yaml.load(f.read())
                        for key, regions in excel_config.items():
                            new_values = []
                            for value in regions:
                                if 'template' in value:
                                    template_path = os.path.join(os.path.dirname(config_abs_path), 'default.yml')
                                    if os.path.isfile(template_path):
                                        with open(template_path) as f2:
                                            template = yaml.load(f2.read())
                                            if value['template'] in template:
                                                new_values.append(dict(template[value['template']], **value))
                                            else:
                                                raise
                                    else:
                                        raise
                                else:
                                    new_values.append(value)
                            excel_config[key] = new_values
                        return [excel_abs_path, excel_config]
                else:
                    # 不执行解析
                    return [excel_abs_path, config_abs_path]

    @staticmethod
    def scan_only(paths):
        """
        解析传入目录下的所有.yml配置文件。

        返回 (excel_abs_path, excel_cfg)的list.
        """
        paths = [_path if os.path.isabs(_path) else os.path.abspath(_path)
                 for _path in paths]
        results = []
        # 处理.yml
        for name in [ i for i in paths if i.endswith('.yml')]:
            result = Commander.detect_data(name, False)
            if result:
                results.append(result)

        # 处理目录
        paths = [i for i in paths if not i.endswith('.yml')]
        def visit(arg, dirname, names):
            for name in [i for i in names if i.endswith('.yml')]:
                result = Commander.detect_data(os.path.join(dirname, name), False)
                if result:
                    results.append(result)

        for path in paths:
            os.path.walk(path, visit, {})
        return results

    def scan_for_data(self, paths):
        """
        解析传入目录下的所有.yml配置文件。

        返回 (excel_abs_path, excel_cfg)的list.
        """
        paths = [_path if os.path.isabs(_path) else os.path.abspath(_path)
                 for _path in paths]
        results = []
        # 处理.yml
        for name in [ i for i in paths if i.endswith('.yml')]:
            result = Commander.detect_data(name)
            if result:
                results.append(result)

        # 处理目录
        paths = [i for i in paths if not i.endswith('.yml')]
        def visit(arg, dirname, names):
            for name in [i for i in names if i.endswith('.yml')]:
                result = Commander.detect_data(os.path.join(dirname, name))
                if result:
                    results.append(result)

        for path in paths:
            os.path.walk(path, visit, {})
        return results

    def load_data(self):
        self._raw = []
        for excel_abs_path, excel_config in self._data:
            loader = ExcelLoader(excel_abs_path, excel_config)
            for meta, unit_datas in loader.load():
                raw_unit = (meta, unit_datas)
                self._raw.append(raw_unit)

    def do_extend(self):
        # 加载所有计算值，包含extend及evals
        for meta, unit_datas in self._raw:
            compute_unit(meta, unit_datas)

    def do_base_correct(self):
        for meta, unit_datas in self._raw:
            correct_unit(meta, unit_datas, meta['fields'])

    def do_correct(self):
        for meta, unit_datas in self._raw:
            correct_unit(meta, unit_datas)

    def do_validation(self):
        for meta, unit_datas in self._raw:
            validate_unit(meta, unit_datas)

    def do_group_validation(self):
        for meta, unit_datas in self._raw:
            exec_group_validation(unit_datas, meta['validation'])

    def do_row_validation(self):
        self.sync_object()
        for meta, unit_datas in self._raw:
            exec_row_validation(unit_datas, meta['validation_row'])

    def do_row_correction(self):
        self.sync_object()
        for meta, unit_datas in self._raw:
            exec_row_correction(unit_datas, meta['correction_row'])

    def do_sample_validation(self, verbose=True):
        errors = []
        self.sync_object()
        for meta, unit_datas in self._raw:
            _errors = exec_sample_validation(unit_datas, meta['sample'])
            if len(_errors)>0:
                if verbose: 
                    print u'文件{}数据遗失了{}条'.format(meta['__src'], len(errors))
                for error in _errors:
                    if verbose:
                        print error
                    errors.append(u'{}: {}'.format(meta['__src'], error))
        return errors

    def do_count_validation(self, verbose=True):
        errors = []
        self.sync_object()
        for meta, unit_datas in self._raw:
            _errors = exec_count_validation(unit_datas, meta['count'])
            if len(_errors)>0:
                if verbose:
                    print u'文件{}数据量不匹配：'.format(meta['__src'], len(errors))
                for error in _errors:
                    if verbose:
                        print error
                    errors.append(u'{}: {}'.format(meta['__src'], error))
        return errors


    def sync_object(self):
        for meta, unit_datas in self._raw:
            for row_data in unit_datas:
                row_data['obj'] = {}
                for col_data in itertools.chain(row_data['raw'], row_data['extend'], row_data['eval']):
                    key = col_data['key']
                    value = col_data['value']
                    row_data['obj'][key] = value

    def do_save_to_excel(self):
        save(self._raw)

    def manual_set(self, col_data, value):
        correct_col_data_value(col_data, value)

    def str_item(self, row_data, html=False):
        link_str = '<br>' if html else '\n'
        msg = link_str
        msg += '-'*20
        columns = [(item['key'], item['value']) for item in itertools.chain(row_data['raw'], row_data['extend'], row_data['eval'])]
        def parse_item(item):
            val = stringify(item[1])
            if val == '':
                val = ' '
            return (item[0], val)

        columns = [item for item in itertools.imap(parse_item, columns)]
        msg += link_str
        msg += u'第{0}行: '.format(row_data['row'])
        msg += link_str
        msg += '|'.join([item[0] for item in columns])
        msg += link_str
        msg += '|'.join([item[1] for item in columns])
        return msg

    def str_item_error(self, row_data, loggers=['validation'], html=False):
        link_str = '<br>' if html else '\n'
        msg =u'错误信息:'
        for logger in loggers:
            msg += link_str
            msg += u'--- 错误类型：{0} ---'.format(logger)
            errors = get_logger(logger, row_data)
            if errors and len(errors)>0:
                msg += link_str
                msg += ';'.join(errors)
            for col_data in itertools.chain(row_data['raw'], row_data['eval'], row_data['extend']):
                errors = get_logger(logger, col_data)
                if errors and len(errors)>0:
                    msg += link_str
                    msg += '%s: %s' % (col_data['key'], ';'.join(errors))
        return msg

    def str_meta(self, meta):
        return '%s: %s (%s)' % (meta['__src'], meta['__src_sheet'], meta['__src_region'])

    def echo_error(self, loggers=['validation']):
        error_total = 0
        for meta, error_items in self._raw:
            print self.str_meta(meta)
            for row_data in error_items:
                error_count = 0
                for logger in loggers:
                    errors = get_logger(logger, row_data)
                    error_count += len(errors) if errors else 0
                    for col_data in itertools.chain(row_data['raw'], row_data['eval'], row_data['extend']):
                        errors = get_logger(logger, col_data)
                        error_count += len(errors) if errors else 0
                if error_count>0:
                    error_total += error_count
                    print self.str_item(row_data)
                    print self.str_item_error(row_data, loggers=loggers)
        print u'错误记录条数: {0}'.format(error_total)
        
    def filter_error_logs(self, loggers=['validation'], html=True):
        result = {}
        error_rows = []
        for meta, error_items in self._raw:
            key = self.str_meta(meta)
            _errors = []
            for row_data in error_items:
                error_count = 0
                for logger in loggers:
                    errors = get_logger(logger, row_data)
                    error_count += len(errors) if errors else 0
                    for col_data in itertools.chain(row_data['raw'], row_data['eval'], row_data['extend']):
                        errors = get_logger(logger, col_data)
                        error_count += len(errors) if errors else 0
                if error_count>0:
                    msg = self.str_item(row_data, html=html)
                    msg = msg + '<br>' + self.str_item_error(row_data, loggers=loggers, html=html)
                    _errors.append(msg)
                    error_rows.append(row_data['row'])
            result[key] = _errors
        return result, error_rows
                
    def summary(self, loggers=['validation'] ,save=False):
        summary = {
            'error': 0,
            'warning': 0,
            'error-obj': 0,
            'obj': 0
        }
        summary['obj'] = reduce(operator.add, [len(unit_datas) for meta, unit_datas in self._raw], 0)
        for meta, row_datas in self._raw:
            for row_data in row_datas:
                error_count = 0
                for logger in loggers:
                    errors = get_logger(logger, row_data)
                    error_count += len(errors) if errors else 0
                    for col_data in itertools.chain(row_data['raw'], row_data['eval'], row_data['extend']):
                        errors = get_logger(logger, col_data)
                        error_count += len(errors) if errors else 0
                if error_count > 0:
                    summary['error'] += error_count
                    summary['error-obj'] += 1
        if save:
            for key in summary.keys():
                self._summary[key].append(summary[key])
        return summary

    def loop_error_item(self, loggers=['validation']):
        for meta, unit_datas in self._raw:
            error_datas = []
            for row_data in unit_datas:
                error_count = 0
                for logger in loggers:
                    errors = get_logger(logger, row_data)
                    error_count += len(errors) if errors else 0
                    for col_data in itertools.chain(row_data['raw'], row_data['eval'], row_data['extend']):
                        errors = get_logger(logger, col_data)
                        error_count += len(errors) if errors else 0
                if error_count>0:
                    error_datas.append(row_data)
            if len(error_datas)>0:
                yield meta, error_datas

    def do_save_to_mysql(self):
        save2mysql(self._raw)
