#-*- coding:utf-8 -*-
# pystol
# Copyright 2012 Jun Kimura
# LICENSE MIT

from os.path import dirname, abspath, join

DEFAULT_PORT = 8080
DEFAULT_ADDRESS = '127.0.0.1' 
DB_PATH = join(dirname(abspath(__file__)), u'db')
SERVER_ADDRESS = (str(DEFAULT_ADDRESS), int(DEFAULT_PORT))
PID_PATH = '/tmp/pystol.pid'
INDEX_PATH = '/tmp/pystol.idx'
# 推測する文字コードのリスト
CODE_LIST = ('utf8', 'shift-jis', 'cp932', 'euc-jp')
# 解析除外MIMEリスト
EXCLUDE_MIME = ('application/octet-stream',)