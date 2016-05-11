# -*- coding: utf-8 -*-
import os
import itertools

from openpyxl import load_workbook

from loader.helper import get_sheet_regions, get_sheets, get_evals
from logger import debug, error
from model import get_correct_rules_by_attr_label, get_attrs_with_validate_rules
from process import exec_correction, exec_evaluation, exec_validation
from util import log, clear_logger_by_row, sync_object_by_rows

def compute_unit(meta, unit_items):
    model_name = meta['model_name']
    evals = meta['evals']
    extend = meta['extend']
    
    for row_item in unit_items:
        row_item['extend'] = []
        row_item['eval'] = []
        if extend:
            for key, value in extend.items():
                row_item['extend'].append({
                    'key': key,
                    'value': value
                })
        sync_object_by_rows([row_item])
        for attr_label, formulas in get_evals(evals):
            errors, warnings, value = exec_evaluation(row_item['obj'], attr_label,
                                                      formulas)
            col_item = {
                'key': attr_label,
                'value': value
            }
            log('eval', col_item, errors)
            log('eval-warning', col_item, warnings)
            row_item['eval'].append(col_item)
            sync_object_by_rows([row_item])


