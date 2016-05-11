# -*- coding: utf-8 -*-

from config import new_mysql_connect

class IDNameLinker(object):

    def __init__(self, standards):
        self._db = standards

    def get_equal_value(self, name):
        for key, value in self._db.items():
            if value == name:
                return {'id': key, 'name': value}

    def correct_name(self, name):
        name = name.replace(u'（', '(').replace(u'）', ')')
        name = name.replace(u'(较高收费)', '').replace(u'(较高学费)', '')
        name = name.replace(u'(中外合作办学)', '')
        name = name.replace(u'(对外合作办学)', '')
        return name

    def get_possible_values(self, name):
        equal_obj = self.get_equal_value(name)
        if equal_obj:
            return [equal_obj]
        correct_name = self.correct_name(name)
        if correct_name != name:
            equal_obj = self.get_equal_value(correct_name)
            if equal_obj:
                return [equal_obj]
        return []

class IDNameSelector(object):

    def __init__(self, table_name, id_field, name_field):
        self._values = {}
        sql = "select {0}, {1} from {2}".format(id_field, name_field, table_name)

        db = new_mysql_connect()
        cursor = db.cursor()
        try:
            cursor.execute(sql)
            results = cursor.fetchall()
            for row in results:
                self._values[str(row[0])] = row[1]

        finally:
            cursor.close()
            db.close()

    def get_all(self):
        return self._values


