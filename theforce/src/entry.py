# -*- coding: utf-8 -*-
import sys
import os.path
import itertools
import operator

import yaml
import MySQLdb
from openpyxl import load_workbook
from pymongo.mongo_client import MongoClient

import config
from loader import ExcelLoader
from model import get_attrs, get_collection
from logger import echo_header


class Commander(object):
    def __init__(self, paths):
        self._path = paths
        self._data = self.scan_for_data(paths)

    def scan_for_data(self, paths):
        """
        解析传入目录下的所有.yml配置文件。

        返回 (excel_abs_path, excel_cfg)的list.
        """
        paths = [_path if os.path.isabs(_path) else os.path.abspath(_path)
                 for _path in paths]
        results = []

        def visit(arg, dirname, names):
            for name in [i for i in names if i.endswith('.yml')]:
                excel_name = "{0}.xlsx".format(name[:-4])
                excel_abs_path = os.path.join(dirname, excel_name)
                config_abs_path = os.path.join(dirname, name)
                if os.path.isfile(excel_abs_path) and os.path.isfile(
                        config_abs_path):
                    with open(config_abs_path) as f:
                        excel_config = yaml.load(f.read())
                        results.append([excel_abs_path.decode('utf-8'), excel_config])

        for path in paths:
            os.path.walk(path, visit, {})
        return results

    def load(self):
        batch_results = []
        for excel_abs_path, excel_config in self._data:
            loader = ExcelLoader(excel_abs_path, excel_config)
            batch_results.extend([results for results in loader.load()])
        return batch_results

    def summary(self, batch_results):
        summary = {
            'error': 0,
            'warning': 0,
            'error-obj': 0,
            'warning-obj': 0,
            'obj': 0
        }
        for results in batch_results:
            for name, objs in results:
                summary['obj'] += len(objs)
                for obj in objs:
                    if '__errors' in obj and len(obj['__errors']) > 0:
                        summary['error'] += len(obj['__errors'])
                        summary['error-obj'] += 1
                    if '__warnings' in obj and len(obj['__warnings']) > 0:
                        summary['warning'] += len(obj['__warnings'])
                        summary['warning-obj'] += 1
        return summary

    def echo_summary(self,
                     batch_results,
                     summary,
                     is_verbose_error=True,
                     is_verbose_warning=False):
        if is_verbose_warning and summary['warning'] > 0:
            echo_header(u'警告信息')
            if summary['warning'] == 0:
                print u'共0个警告信息。'
            else:
                print u'共{0}个警告信息，发生在{1}条数据里。'.format(summary['warning'],
                                                      summary['warning-obj'])
                for results in batch_results:
                    for model_name, objs in results:
                        for obj in objs:
                            if len(obj['__warnings']) > 0:
                                print '*' * 30
                                print u'{0} - {1} - 行{2}:'.format(
                                    obj['__src'], obj['__src_sheet'],
                                    obj['__src_row'])
                                print '\n'.join(obj['__warnings'])
                                print

        if is_verbose_error and summary['error'] > 0:
            echo_header(u'错误信息')
            if summary['error'] == 0:
                print u'共0个错误信息。'
            else:
                print u'共{0}个错误信息，发生在{1}条数据里。'.format(summary['error'],
                                                      summary['error-obj'])
                for results in batch_results:
                    for model_name, objs in results:
                        for obj in objs:
                            if len(obj['__errors']) > 0:
                                print '*' * 30
                                print u'{0} - {1} - 行{2}:'.format(
                                    obj['__src'], obj['__src_sheet'],
                                    obj['__src_row'])
                                print '\n'.join(obj['__errors'])
                                print

        echo_header('Summary')
        print u"数据量:", summary['obj']
        print u"错误(数据数/信息数): {0}/{1}".format(summary['error'],
                                             summary['error-obj'])
        print u"警告(数据数/信息数): {0}/{1}".format(summary['warning'],
                                             summary['warning-obj'])

    def on_load(self):
        batch_results = self.load()
        summary = self.summary(batch_results)
        self.echo_summary(batch_results, summary)
        return batch_results, summary['error'] > 0

    def on_stash(self):
        batch_results, is_error = self.on_load()
        if not is_error:
            echo_header(u'Save to Mongo')
            mongo = MongoClient(**config.mongo)
            summary = {}
            try:
                for results in batch_results:
                    for model_name, objs in results:
                        for collection_name, group_objs in itertools.groupby(
                                objs,
                                lambda obj: get_collection(model_name, obj)):
                            group_objs = [obj for obj in group_objs]
                            db = mongo.get_database('theforce')
                            collection = db.get_collection(collection_name)
                            collection.insert_many(group_objs)
                            summary[collection_name] = len(
                                group_objs) if collection_name not in summary else len(
                                    group_objs) + summary[collection_name]
                echo_header(u'Mongo结果')
                print u"数据已成功保存到MongoDB的theforce库中，其中新增数据:"
                for name, length in summary.items():
                    print name, length
            finally:
                mongo.close()


if __name__ == "__main__":
    fn = sys.argv[1]
    paths = sys.argv[2:]
    commander = Commander(paths)

    if fn == 'check':
        commander.on_load()
    elif fn == 'stash':
        commander.on_stash()
    elif fn == 'save':
        print 'TODO'
