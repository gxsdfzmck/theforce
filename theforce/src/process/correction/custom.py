# -*- coding: utf-8 -*-

wenke_labels = [u'文科', u'文', u'文科综合', u'文史', u'文史类']
like_labels = [u'理科', u'理', u'理科综合', u'理工', u'理工类']

def subject_name(input):
    if input is None:
        return None
    try:
        wenke_labels.index(input)
    except:
        pass
    else:
        return u'文科'
    try:
        like_labels.index(input)
    except:
        pass
    else:
        return u'理科'

    return input

def year(input):
    if input is None:
        return None
    if type(input) == unicode or type(input) == str:
        if input.endswith(u'年'):
            return input[:len(input)-1]
    return input
