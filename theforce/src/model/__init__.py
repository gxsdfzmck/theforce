# -*- coding: utf-8 -*-
import os
import itertools

from .repo import Repository
from util import sync_object_by_rows


def new_repository_instance():
    directory = os.path.join(os.path.dirname(__file__), '../../data/models')
    abs_paths = []

    def visit(arg, dirname, names):
        abs_paths.extend([os.path.join(dirname, name)
                          for name in names if name.endswith('.yml')])

    os.path.walk(directory, visit, {})

    return Repository(abs_paths)


repository = new_repository_instance()


def is_model_exists(model_name):
    return repository.get(model_name) is None


def get_attrs(model_name):
    model_meta = repository.get(model_name)
    if model_meta and 'attributes' in model_meta:
        for attr_label, attr_meta in model_meta['attributes'].items():
            yield attr_label, attr_meta['name'], attr_meta


def get_collection(model_name, context):
    model_meta = repository.get(model_name)
    if model_meta and 'collection' in model_meta:
        return model_meta['collection']


def get_model_attr(model_name, attr_label):
    model_meta = repository.get(model_name)
    if model_meta and 'attributes' in model_meta and attr_label in model_meta[
            'attributes']:
        return model_meta['attributes'][attr_label]


def get_correct_rules_by_attr_label(model_name, attr_label):
    attr_meta = get_model_attr(model_name, attr_label)
    if attr_meta:
        if 'correction' in attr_meta:
            return attr_meta['correction']


def get_validate_rules_by_attr_label(model_name, attr_label):
    attr_meta = get_model_attr(model_name, attr_label)
    if attr_meta:
        if 'validation' in attr_meta:
            return attr_meta['validation']


def get_attrs_with_validate_rules(model_name):
    for attr_label, attr_name, attr_meta in get_attrs(model_name):
        yield attr_label, attr_name, get_validate_rules_by_attr_label(
            model_name, attr_label)


def convert2tabledatas(model_name, row_datas):
    model_meta = repository.get(model_name)
    if model_meta is None:
        return
    persist_attrs = []
    if 'attributes' in model_meta:
        for attr_label, attr_meta in model_meta['attributes'].items():
            if 'transient' in attr_meta and attr_meta['transient']:
                continue
            default_value = attr_meta[
                'default'] if 'default' in attr_meta else None
            persist_attrs.append([attr_label, attr_meta['name'], default_value
                                  ])
    if len(persist_attrs) == 0:
        return

    table_name = model_meta['table']
    column_names = [persist_attr[1] for persist_attr in persist_attrs]
    column_labels = [persist_attr[0] for persist_attr in persist_attrs]

    sync_object_by_rows(row_datas)

    def group_fn(row_data):
        obj = row_data['obj']
        try:
            return eval(table_name)
        except Exception, e:
            raise e

    for _table_name, items in itertools.groupby(row_datas, group_fn):
        table_datas = []
        for row_data in items:
            table_data = [ row_data['obj'][attr_meta[0]]
                           if attr_meta[0] in row_data['obj'] and row_data['obj'][attr_meta[0]] is not None
                           else attr_meta[2] for attr_meta in persist_attrs ]
            table_datas.append(table_data)
        yield _table_name, column_names, table_datas
