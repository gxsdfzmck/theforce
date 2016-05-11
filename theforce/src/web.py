# -*- coding: utf-8 -*-
import datetime
import os
import itertools

from flask import Flask, render_template, request, json

from command import Commander

app = Flask(__name__)

config = {
    'dir_path': u'G:\practice\数据目录'
}
context = {}

@app.route('/', methods=['GET'])
def main():
    return render_template('main.html')

@app.route('/fs', methods=['GET'])
def get_files():
    root = {'label': config['dir_path'], 'children': []}

    results = Commander.scan_only([config['dir_path']])
    files = sorted([ os.path.relpath(yaml, config['dir_path']) for excel,yaml in results ])
    for group_name, group_items in itertools.groupby(files, lambda filename: os.path.split(filename)[0]):
        child = {'label': group_name}
        child['children'] = [{'label': os.path.split(filename)[1], 'value':filename} for filename in group_items]
        root['children'].append(child)

    return json.dumps(root)

@app.route('/check', methods=['POST'])
def check():
    results = []

    request_data = request.get_json()
    args = request_data['fs']
    # args = u'24.吉林/2014_院校专业'
    files = [ os.path.join(config['dir_path'], p) for p in args.strip().split(',')]

    for index, filename in enumerate(files):
        commander = Commander([filename])
        commander.load_data()
        # 基础校验
        commander.do_base_correct()
        commander.do_extend()
        commander.do_correct()
        commander.do_validation()
        error_basic, error_basic_rows = commander.filter_error_logs(loggers=['validation'])
        # 行级校验
        commander.do_row_correction()
        commander.do_row_validation()
        error_row, error_row_rows = commander.filter_error_logs(loggers=['validation_row'])
        # 全局校验
        commander.do_group_validation()
        error_global, error_global_rows = commander.filter_error_logs(loggers=['order', 'duplicate', 'continuous_unique'])
        # 抽样校验
        error_sample = commander.do_sample_validation(verbose=False)
        # 数据量校验
        error_count = commander.do_count_validation(verbose=False)

        count = {
            'number': len(error_count),
            'sample': len(error_sample),
            'basic': sum([len(i) for i in error_basic.values()],0),
            'row': sum([len(i) for i in error_row.values()],0),
            'global': sum([len(i) for i in error_global.values()],0)
        }
        count['total'] = sum(count.values())


        list_rows = sorted(set(error_basic_rows + error_row_rows))
        list_danger = sorted(set(error_global_rows))
        msg = {}
        msg['rows'] = ','.join([str(i) for i in list_rows]) if len(list_rows)>0 else u'无'
        msg['danger'] = ','.join([str(i) for i in list_danger]) if len(list_danger)>0 else u'无'

        results.append({
            'id': index,
            'name': os.path.split(filename)[1],
            'filename': filename,
            'time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'count': count,
            'msg': msg,
            'number': '<br>'.join(error_count),
            'sample': '<br>'.join(error_sample),
            'basic': '<br>'.join(list(itertools.chain(*error_basic.values()))),
            'row': '<br>'.join(list(itertools.chain(*error_row.values()))),
            'global': '<br>'.join(list(itertools.chain(*error_global.values())))
        })

    return json.dumps(results)

if __name__ == '__main__':
    app.run(debug=True)
