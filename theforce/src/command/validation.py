# -*- coding: utf-8 -*-
import os
import itertools

from openpyxl import load_workbook

from loader.helper import get_sheet_regions, get_sheets, get_evals
from logger import debug, error
from model import get_correct_rules_by_attr_label, get_attrs_with_validate_rules
from process import exec_validation
from util import get_col_data_by_attr_name, log, clear_logger_by_row


def validate_unit(meta, unit_datas):
    for row_item in unit_datas:
        clear_logger_by_row('validation', row_item)
        validate(meta, row_item)

def validate(meta, row_item):
    model_name = meta['model_name']
    for attr_label, attr_name, validation in get_attrs_with_validate_rules(
            model_name):
        if attr_label not in meta['disable_validation']:
            if validation and len(validation)> 0:
                col_item = get_col_data_by_attr_name(row_item, attr_label)

                errors = exec_validation(attr_label, col_item, validation)
                if len(errors)>0:
                    log('validation', col_item if col_item else row_item, errors)


