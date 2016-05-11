# -*- coding: utf-8 -*-
import pymysql

mongo = {'host': 'localhost', 'port': 27017}
mysql = {
    'host': 'mysql.tobeornot.cn',
    'user': 'wutdev',
    'passwd': 'o4mo7XGgweycVe9WTVxg',
    'database': 'raw_data',
    'charset': 'utf8',
    'autocommit': True
}

def new_mysql_connect():
    return pymysql.connect(**mysql)

