#-*- coding:utf-8 -*-
# pystol
# Copyright 2012 Jun Kimura
# LICENSE MIT

from lib.constant import CODE_LIST
from functools import wraps
from zlib import compress, decompress
import os, sys, logging
try:
    import cPickle as pickle
except:
    import pickle
try:
    import simplejson as json
except:
    import json
dumps = json.dumps
loads = json.loads
    
logger = None

def set_logger():
    global logger
    logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s (%(threadName)-2s) %(message)s',
                    #filename='/tmp/twipy.log',
                    #filemode='w'
                    )
    logger = logging.getLogger("server")

def guess_encode(text):
    '''
    @summary: Unicode型をstr型にencodeします
    @param text: str
    @return: unicode
    '''
    for enc in CODE_LIST:
        try:
            return text.encode(enc)
        except:
            pass
    logger.error(u"Can't encode")
    raise Exception("Encode Error.")
    
def guess_decode(text):
    '''
    @summary: str型をUnicode型にdecodeします
    @param text: str
    @return: unicode
    '''
    for dec in CODE_LIST:
        try:
            return text.decode(dec)
        except:
            pass
    logger.error("Can't decode")
    raise Exception("Decode Error.")

def to_utf8(text):
    return text.encode('utf8')

def daemonize(pidfile, daemonfunc, *args, **kw):
    try:
        pid = os.fork()
        if (pid > 0):
            sys.exit(0)
    except OSError:
        print >>sys.stderr, 'daemonize: fork #1 failed.'
        sys.exit(1)
 
    try:
        os.setsid()
    except:
        print >>sys.stderr, 'daemonize: setsid failed.'
        sys.exit(1)
 
    try:
        pid = os.fork()
        if (pid > 0):
            sys.exit(0)
    except OSError:
        print >>sys.stderr, 'daemonize: fork #2 failed.'
        sys.exit(1)
 
    try:
        f = file(pidfile, 'w')
        f.write('%d' % os.getpid())
        f.close()
    except IOError:
        print >>sys.stderr, 'daemonize: failed to write pid to %s' % pidfile
        sys.exit(1)

    try:
        os.chdir('/')        
        os.umask(0)
        sys.stdin = open('/dev/null', 'r')
        sys.stdout = open('/dev/null', 'w')
        sys.stderr = open('/dev/null', 'w')
    except:
        pass
 
    daemonfunc(*args, **kw)
    
def synchronized(f):
    @wraps(f)
    def _syncronized(self, *args, **kw):
        with self.LOCK:
            return f(self, *args, **kw)
    return _syncronized

def jz_dump(data):
    ''' json & zlib　圧縮'''
    return compress(dumps(data))

def jz_load(data):
    ''' json & zlib 解凍'''
    return loads(decompress(data))
        
def setup():
    set_logger()
    
setup()

