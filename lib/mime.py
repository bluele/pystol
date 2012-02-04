#-*- coding:utf-8 -*-
# pystol
# Copyright 2012 Jun Kimura
# LICENSE MIT
try:
    import magic
except ImportError:
    raise
import re

pattern = {}
# PDFファイルからテキストを抽出します
from_pdf = None
# ファイルからテキストを抽出します
from_doc = None

def setup():
    pattern['pdf'] = re.compile("^PDF")

class Mime(object):
    '''
    @summary: MIME Typeを扱うクラス
    '''
    def __init__(self):
        self._mime = magic.Magic(mime=True)
        
    def from_file(self, path):
        return self._mime.from_file(path)
    
setup()