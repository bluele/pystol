#-*- coding:utf-8 -*-
# pystol
# Copyright 2012 Jun Kimura
# LICENSE MIT

from lib.util import *
from lib.index import MasterIndex, pickle
from lib.observer import Watcher
from lib.error import AlreadyAddPathError, NotFoundPathError
from multiprocessing import Process
import SocketServer
import os


class RequestMethodMixIn():

    def add(self, path, recursive=True):
        '''
        @summary: 指定されたパスをインデックス化して追加し、パスを監視パスに追加する。
        @return: str: response
        '''
        try:
            self.watcher.schedule(path, recursive)
        except AlreadyAddPathError:
            return "AlreadyAddPathError"
        else:
            return "Add %s" % os.path.abspath(path)
        
    def remove(self, path):
        '''
        @summary: 監視パスから外す & インデックスから除去
        '''

    def find(self, query):
        '''
        @summary: search query for index
        '''
        path_list = self.watcher.find(query)
        if len(path_list) <= 0:
            return "No such file."
        path = "\n".join(path_list)
        logger.debug(path)
        return path
    

class RequestHandler(SocketServer.BaseRequestHandler, RequestMethodMixIn):
    ''' @summary: TCPServerのリクエストハンドラ'''

    def __init__(self, request, client_address, server):
        self.request = request
        self.client_address = client_address
        self.server = server
        self.setup()
        try:
            self.handle()
        finally:
            self.finish()

    def setup(self):
        return SocketServer.BaseRequestHandler.setup(self)

    def handle(self):
        logger.debug("connect by %s" % str(self.client_address))
        try:
            data = self.request.recv(8192)
            if data != "":
                try:
                    response = self.dispatch(data)
                except Exception, err:
                    response = err
                self.request.send(str(response))
            else:
                self.request.send("Fatal Error: Don't Catch Any Data.")
        except Exception, err:
            raise
        logger.debug("server: connection close")
       
    def dispatch(self, data):
        '''
        @summary: Dispatch received data
        @return: str: response
        ''' 
        response = ""
        try:
            d = pickle.loads(data)
            if d['method'] == 'ADD':
                response = self.add(d['content'])
            elif d['method'] == 'REMOVE':
                response = self.remove(d['content'])      
            elif d['method'] == 'FIND':
                response = self.find(d['content'])
            elif d['method'] == 'UPDATE':
                response = self.update(d['content'])
            else:
                raise Exception("'%s' is unknown method." % (d['method'],))
        except pickle.PicklingError, err:
            response = err
        except Exception, err:
            response = err
        return response

    def finish(self):
        return SocketServer.BaseRequestHandler.finish(self)


class PystolServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    '''
    @summary: メインサーバー
    '''
    
    def __init__(self, server_address, handler_class=RequestHandler):
        self.watcher = Watcher(MasterIndex())
        handler_class.watcher = self.watcher
        SocketServer.TCPServer.__init__(self, server_address, handler_class)
    
    def run(self, daemon=False):
        '''
        @summary: run server
        @param daemon: bool
        '''
        self.watcher.start()
        logger.debug("start watch server.")
        if daemon:
            Process(target=self.serve_forever).start()
        else:
            self.serve_forever()
        
    def stop(self):
        '''
        @summary: サーバーの停止メソッドです
        @todo: 終了処理を行う
        '''
        self.shutdown()
    