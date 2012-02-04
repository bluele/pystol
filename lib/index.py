#-*- coding:utf-8 -*-
# pystol
# Copyright 2012 Jun Kimura
# LICENSE MIT

from lib.error import NotMatchQuery
from lib.constant import *
from lib.util import *
#from multiprocessing import RLock
from threading import RLock
import os, socket
try:
    import cPickle as pickle
except:
    import pickle
    
class AbstractIndex(object):
    ''' 
    @summary: indexの規定クラス
    @todo: すべてのファイルは自分のファイル名を先頭に含める　バイナリはファイル名のみtermとする
    '''
    
    def __init__(self, n=2, m=3):
        self._index = {}
        self.n = n
        self.m = m
            
    def _add(self, path, text):
        '''
        @summary: インデックス追加の実装クラス
        '''
        if len(text) < self.n:
            if not self._index.has_key(text):
                self._index[text] = {}
            if not self._index[text].has_key(path):
                self._index[text][path] = []
        cur = 0
        while(len(text) >= cur + self.n):
            token = text[cur:cur+self.n]
            if not self._index.has_key(token):
                self._index[token] = {}
            if not self._index[token].has_key(path):
                self._index[token][path] = set()
            # append follower
            for i in range(self.m):
                pref = cur + i + 1
                follow = text[pref:pref+self.n]
                if len(follow) == 0:
                    continue
                self._index[token][path].add(follow)
            cur += 1
            
    def remove(self, path_list):
        '''
        @summary: インデックスから指定したパスを含むインデックスを削除する
        '''
        dels = set()
        for term, index in self._index.iteritems():
            for path in index.keys():
                if path in path_list:
                    dels.add((term, path))
        for term, path in dels:
            del self._index[term][path]
              
    def search(self, text):
        '''
        @summary: 検索メソッド
        @return: set
        '''
        query = list(self.ingram(text.lower()))
        match_set = set()
        try:
            pref = query.pop(0)
            if self._index.has_key(pref):
                for path, follower in self._index[pref].iteritems():
                    #logger.debug("%s - %s - %s" % (pref, path, u":".join(follower)))
                    try:
                        for q in query[:self.m]:
                            if not q in follower:
                                raise NotMatchQuery
                    except NotMatchQuery:
                        continue
                    except IndexError:
                        continue
                    else:
                        match_set.add(path)
            # クエリにマッチするインデックスがない場合
            else:
                pass
        except IndexError:
            raise
        except:
            raise
        return match_set
    
    def ingram(self, text):
        cur = 0
        if len(text) == 1:
            yield text[0]
        while(len(text) >= cur + self.n):
            yield text[cur:cur + self.n]
            cur += 1
    
    def load(self):
        ''' @summary: indexの読み込み'''
        if os.path.isfile(INDEX_PATH):
            with open(INDEX_PATH, 'rb') as f:
                self._index = pickle.load(f)
    
    def save(self):
        ''' @summary: indexの保存'''
        with open(INDEX_PATH, 'wb') as f:
            pickle.dump(self._index, f)


class MasterIndex(AbstractIndex):
    '''
    @summary: 
        マスターインデックス
        各スレッドがインデックスを作成してそれをマスターにマージする
    '''
    
    def __init__(self):
        AbstractIndex.__init__(self)
        self.LOCK = RLock()
        self.load()
        
    @synchronized
    def update(self, child):
        '''
        @summary: 
            子インデックスとのマージを行う
            子インデックスが削除情報を持っていた場合、それに従いインデックスから削除
        @warning: dict.updateを行うとtermが重複する際に
        '''
        for term, path in child._index.iteritems():
            if not self._index.has_key(term):
                self._index[term] = {}
            self._index[term].update(path)
        del child
        
class ChildIndex(AbstractIndex):
    '''
    @summary:　サーバーの更新用インデックス
    '''   
    
    def __init__(self):
        # マスターから削除するべきパス
        #self.delete_list = list()
        AbstractIndex.__init__(self)
        
    def add(self, path, text=None):
        ''' 
        @summary: 指定したパスをインデックスに追加する
        @param text: 指定した場合、パスの内容に関係なく、指定した内容をインデックスに追加します
        @todo: デコード処理の例外処理
        '''
        name = os.path.basename(path)
        if text:
            self._add(path, guess_decode(text).lower())
        else:
            with open(path, 'rb') as f:
                text = f.read()
            self._add(path, (guess_decode(name) + guess_decode(text)).lower())
      
    def clear(self):
        ''' @summary: インデックスを空にします ''' 
        self._index = {}
