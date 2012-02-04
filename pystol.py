#-*- coding:utf-8 -*-
# pystol
# Copyright 2012 Jun Kimura
# LICENSE MIT

import socket
from lib.server import PystolServer
from lib.constant import SERVER_ADDRESS
from lib.util import pickle
import optparse

def _command_to_server(method, content=None):
    '''
    @summary: サーバーとの通信を行います
    '''
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(SERVER_ADDRESS)
        sock.send(pickle.dumps(
                        {
                         'method':method,
                         'content':content
                         }
                        ))
        data = ""
        while True:
            resp = sock.recv(8192)
            if not resp:
                break
            data += resp
        if data:
            print data
    except:
        raise
    finally:
        sock.close()

def find(option, opt_str, query, parser):
    '''
    @summary: インデックス内のクエリにマッチするパスを表示します
    '''
    _command_to_server(method="FIND", content=query)

def add(option, opt_str, path, parser):
    '''
    @summary: 
        引数にパスを指定
        パスを解析してインデックスを生成する
    @todo: popenを使って結果を返したりする
    '''
    _command_to_server(method="ADD", content=path)
    
def server_operate(option, opt_str, query, parser):
    '''
    @summary: 起動、停止などに振り分ける
    '''
    if query == 'start':
        return start()
    elif query == 'stop':
        return stop()
    elif query == 'restart':
        return restart()
    raise Exception("Query '%s' is not known." % query)

def start():
    '''
    @summary: メインサーバーの起動メソッド
    '''
    server = PystolServer(SERVER_ADDRESS)
    server.run()
    
def stop():
    '''
    @summary: 
    メインサーバーの停止メソッド
    '''
    _command_to_server(method="STOP")
    
def restart(option, opt_str, value, parser):
    '''
    @summary: メインサーバーの再起動メソッド
    '''
         
def opt_setup():
    parser = optparse.OptionParser()
    # opt for start, stop, restart , etc..
    parser.add_option('-k',
                      #'--add',
                      action="callback",
                      callback=server_operate,
                      nargs=1,
                      type="string",
                      help="Operate Pystol Server.",
                      )
    # opt for add
    parser.add_option('-a',
                      '--add',
                      action="callback",
                      callback=add,
                      nargs=1,
                      type="string",
                      help="Add directory path in Index.",
                      )

    # opt for find
    parser.add_option('-f',
                      '--find',
                      action='callback',
                      callback=find,
                      nargs=1,
                      type="string",
                      help="Find file path in Index",
                      )
    
    options, args = parser.parse_args()

if __name__ == '__main__':
    opt_setup()
    
