#-*- coding:utf-8 -*-
# pystol
# Copyright 2012 Jun Kimura
# LICENSE MIT

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from lib.index import ChildIndex
from lib.util import logger, synchronized, guess_decode
from lib.error import AlreadyAddPathError, NotFoundPathError
from lib.mime import Mime, pattern
from lib.constant import EXCLUDE_MIME
from threading import RLock
import os
import re
from os.path import isdir, abspath, exists


class SyncEventHandler(FileSystemEventHandler):
    '''
    @summary:
    ファイルシステムのイベントを制御
    更新があったファイルパスを取得し、インデックスを操作する
    '''
    
    def __init__(self, watcher):
        self.watcher = watcher
        FileSystemEventHandler.__init__(self)
        
    def refresh_file(self, path):
        '''
        @summary: 指定したファイルパスのインデックスを更新します
        '''
        self.watcher.index.remove([path])
        self.watcher.analyze_file(path)
        #logger.debug("REFRESH %s" % path)

    def on_created(self, event):
        '''
        @summary:
            新規作成時イベント
            新規ファイルのインデックスを追加する
        '''
        if event.is_directory:
            self.watcher.analyze_dir(event.src_path, True)
        else:
            self.watcher.analyze_file(event.src_path)
        FileSystemEventHandler.on_created(self, event)

    def on_modified(self, event):
        '''
        @summary:
        ファイル更新時イベント
        ファイルのときはインデックス更新
        ディレクトリのときはファイルが追加されたときとかそういうイベントなので、無視
        '''
        if not event.is_directory:
            self.refresh_file(event.src_path)
        FileSystemEventHandler.on_created(self, event)
        
    def on_deleted(self, event):
        '''
        @summary: ファイル削除イベント
        '''
        if event.is_directory:
            pass
        else:
            self.watcher.index.remove([event.src_path])
        logger.debug("DELETE %s" % event.src_path)
        FileSystemEventHandler.on_deleted(self, event)
        
    def on_moved(self, event):
        '''
        @summary: ファイル移動イベント
        '''
        FileSystemEventHandler.on_moved(self, event)
        

class Watcher(Observer):
    '''
    @summary: WatchdogのAPIをoverrideする インデックスを作成するためにパスを追加する必要がある
    @todo: indexのsearchメソッドを実装
    '''
    
    def __init__(self, index, event_handler=SyncEventHandler):
        self.LOCK = RLock()
        self.pool = []
        self.index = index
        self.watch_path = dict()
        self.event_handler = event_handler(self)
        self.mime = Mime()
        Observer.__init__(self)
        #self.create_scan_thread(count=1)
        
    @synchronized
    def schedule(self, path, recursive=False):
        path = abspath(path)
        try:
            # インデックス追加処理
            self.scan_path(path, recursive)
            self.watch_path[path] = Observer.schedule(self, self.event_handler, path, recursive)
        except NotFoundPathError, err:
            logger.error(err)
            raise
                    
    @synchronized
    def unschedule(self, path):
        ''' 
        @summary: 監視リストから指定したファイルパスを監視するwatchを除去する
                　整理はしていない
        @warning:  Linuxのみwatchスレッドが死んでいない テスト&要修正
        '''
        path = abspath(path)
        Observer.unschedule(self, self.watch_path[path])
        del self.watch_path[path]
        logger.debug("unschedule %s" % path)
        
    def find(self, query):
        '''
        @summary: インデックスから特定のクエリにマッチするパスを返す
        '''
        return self.index.search(guess_decode(query))
        
    def scan_path(self, path, recursive):
        ''' 
        @summary: 指定されたパスを解析します
        '''
        if not exists(path):
            raise NotFoundPathError("Not Found Path.")
        if not isdir(path):
            raise Exception("%s is not directory." % path)
        self.analyze_dir(path, recursive)
    
    def analyze_dir(self, path, recursive):
        '''
        @summary: 監視ディレクトリを既存のものと整理する
        '''
        for wpath, wobj in self.watch_path.iteritems():
            # recursive == True かつ watchの子階層にpathがいれば既に追加済み
            if wobj.is_recursive and re.search(wpath, path):
                raise AlreadyAddPathError
        
        if recursive:
            for root, dirs, files in os.walk(path):
                for dir_name in dirs:
                    dir_path = os.path.join(root, dir_name)
                    if self.watch_path.has_key(dir_path):
                        self.unschedule(dir_path)
                for fname in files:
                    fpath = os.path.join(root, fname)
                    self.analyze_file(fpath)
        else:
            root, dirs. files = os.walk(path).next()
            for dir_name in dirs:
                dir_path = os.path.join(path, dir_name)
                if self.watch_path.has_key(dir_path):
                    self.unschedule(dir_path)
            for fname in files:
                fpath = os.path.join(root, fname)
                self.analyze_file(fpath)
                
    def analyze_file(self, path):
        '''
        @summary:
        ファイル解析
        スレッドに委託するならこのメソッドをワーカーにする
        '''
        try:
            index = ChildIndex()
            # mimeがGC時のバグがある模様
            mtype = self.mime.from_file(path)
            if mtype in EXCLUDE_MIME:
                index.add(path, os.path.basename(path))
                logger.debug("IGNORE: %s" % path)
            # 各パターンごとに判定して、テキスト読取
            elif pattern['pdf'].search(mtype):
                # PDFからテキストを抽出してインデックス追加の第二引数に指定
                index.add(path, os.path.basename(path))
                logger.debug("PDF '%s'" % path)
            else:
                index.add(path)
                logger.debug("ADD Index '%s'" % path)

        except Exception, err:
            logger.error(err)
            #raise
        else:
            self.index.update(index)
        
    