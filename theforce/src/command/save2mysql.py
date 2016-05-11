# -*- coding: utf-8 -*-
import itertools

import MySQLdb

import config
from logger import echo_header, error
from model import repository, convert2tabledatas

def save2mysql(raw_datas, batch_size=100):
    db = MySQLdb.connect(**config.mysql)
    cursor = db.cursor()
    echo_header(u'保存数据到MySQL中')
    try:
        for meta, row_datas in raw_datas:
            # 转化成table_name, obj的形式
            for table_name, column_names, table_rows in convert2tabledatas(meta['model_name'], row_datas):
                sql = "insert into {0}({1}) values({2})".format(
                    table_name, ','.join(['`{0}`'.format(i) for i in column_names]),
                    ','.join(itertools.repeat('%s', len(column_names))))

                table_rows_batches =[[ i for index,i in items] for name, items in itertools.groupby(enumerate(table_rows), lambda it: it[0]/batch_size)]
                echo_header(u'插入数据到表{0}，共{1}条数据，按每批{2}条批量迁移:'.format(table_name, len(table_rows), batch_size))
                for items in table_rows_batches:
                    print '.',
                    cursor.executemany(sql, items)
                print u'完成.'
        db.commit()
    finally:
        cursor.close()
        db.close()


