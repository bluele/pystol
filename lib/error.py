#-*- coding:utf-8 -*-
# pystol
# Copyright 2012 Jun Kimura
# LICENSE MIT

class AlreadyAddPathError(Exception):
    def __init__(self, *args, **kw):
        Exception.__init__(self, *args, **kw)

class NotMatchQuery(Exception):
    def __init__(self, *args, **kw):
        Exception.__init__(self, *args, **kw)

''' @summary: 指定されたパスが存在しないときに吐く'''
class NotFoundPathError(Exception):
    def __init__(self, *args, **kw):
        Exception.__init__(self, *args, **kw)