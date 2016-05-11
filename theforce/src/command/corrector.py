# -*- coding: utf-8 -*-
import os
import itertools

from openpyxl import load_workbook

from loader.helper import get_sheet_regions, get_sheets, get_evals
from logger import debug, error
from model import get_correct_rules_by_attr_label, get_attrs_with_validate_rules, get_attrs
from process import exec_correction, exec_evaluation, exec_validation
from util import get_col_data_by_attr_name, log

def correct_unit(meta, unit_datas, attr_labels=None):
    if attr_labels is None:
        attr_labels = [attr_attrs[0] for attr_attrs in get_attrs(meta['model_name'])]
    for row_item in unit_datas:
        correct(meta, row_item, attr_labels)

def correct(meta, row_item, attr_labels):
    model_name = meta['model_name']
    fields_correct_formula = meta['fields_correct_formula']
    for attr_label in attr_labels:
        col_item = get_col_data_by_attr_name(row_item, attr_label)
        if col_item:
            init_value = col_item['value']
            # 先看fields_correct_formula中是否存在
            if attr_label in fields_correct_formula:
                try:
                    value = eval(fields_correct_formula[attr_label])
                    if value != init_value:
                        col_item['value'] = value
                        if 'raw_value' not in col_item:
                            col_item['raw_value'] = init_value
                            col_item['change'] = True
                        init_value = value
                except Exception,e:
                    pass

            # model 级
            correction = get_correct_rules_by_attr_label(model_name, attr_label)
            errors, warnings, value = exec_correction(attr_label, init_value,
                                                        correction)
            if value != init_value:
                col_item['value'] = value
                if 'raw_value' not in col_item:
                    col_item['raw_value'] = init_value
                col_item['change'] = True
            log('correct',  col_item, errors)
            log('correct-warning', col_item, warnings)

