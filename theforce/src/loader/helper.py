# -*- coding: utf-8 -*-


def get_sheets(excel_config):
    for sheet_name, regions in excel_config.items():
        yield sheet_name, regions


def get_sheet_regions(sheet_config):
    for rcfg in sheet_config:
        model_name = rcfg['model']
        region = '%s:%s' % tuple(rcfg['region'])
        fields = rcfg['fields']
        extend = rcfg['extend'] if 'extend' in rcfg else None
        evals = rcfg['evals'] if 'evals' in rcfg else []
        validation = rcfg['validate'] if 'validate' in rcfg else []
        validation_row = rcfg['validate_row'] if 'validate_row' in rcfg else []
        correction_row = rcfg['correct_row'] if 'correct_row' in rcfg else []
        disable_validation = rcfg['disable_validation'] if 'disable_validation' in rcfg else []
        fields_correct_formula = rcfg['fields_correct_formula'] if 'fields_correct_formula' in rcfg else {}
        sample = rcfg['sample'] if 'sample' in rcfg else []
        count = rcfg['count'] if 'count' in rcfg else []
        yield model_name, region, extend, fields, evals, validation, validation_row, correction_row, disable_validation, fields_correct_formula, sample, count

def get_evals(evals):
    for item in evals:
        yield item['field'], item['eval']
