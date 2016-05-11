# -*- coding: utf-8 -*-
#import sys
#reload(sys)
#sys.setdefaultencoding( "utf-8" )
def debug(msg):
    print 
    print '[DEBUG]',msg

def info(msg):
    print msg
    print 

def warning(msg):
    print msg
    print 

def error(msg):
    print msg
    print 

def echo_header(title):
    print 
    print "="*40
    print title
    print "="*40
    print 

echo_header("mmm")