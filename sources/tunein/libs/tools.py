from default import *

import os
import mc

import unicodedata
import time
import stat
import traceback
import binascii
import bz2
from operator import itemgetter, attrgetter

try: import json
except: import simplejson as json

try:    from hashlib import md5
except: from md5 import md5
import marshal

def urlopen(url, params={}, cache=False):
    """
    Action a http request
    # url - reqest url
    # params - dict,    extra http parameters (optional)
    #        xhr       - boolean,  make a xhr ajax request
    #        post      - dict,     parameters to POST if empty a GET request is executed
    #        cookie    - string,   send cookie data with request
    #        useragent - string,   send custom useragent with request
    # cache - instance, possible to feed a cache instance
    # age   - int,      maximum age in seconds of cached item
    """

    http = mc.Http()
    #http.SetUserAgent("Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.2.13) Gecko/20101206 Ubuntu/10.10 (maverick) Firefox/3.6.13")
    #http.SetHttpHeader('Accept', 'text/javascript, text/html, application/xml, text/xml, */*')

    if cache:
        if params.get('cache', False):
            data = cache.get(url, age=params['cache'])
        else:
            data = cache.get(url)
        if data:
            return data

    if params.get('xhr', False):
        http.SetHttpHeader('X-Requested-With', 'XMLHttpRequest')
    if params.get('cookie', False):
        http.SetHttpHeader('Cookie', params['cookie'])
    if params.get('useragent', False):
        http.SetUserAgent(params['useragent'])

    if params.get('post', False):
        data = http.Post(url, params['post'])
    else:
        data = http.Get(url)

    if cache:
        if params.get('cache', False):
            cache.set(url, data)

    return data

def ConvertASCII(string):
    """
    Function to convert special characters to regular unicode characters (python 2.4)
    string - string to check
    """
    return unicodedata.normalize('NFKD', string.decode('utf-8')).encode('ascii','ignore')


def encodeUTF8(string):
    """
    Function to convert string to utf-8 if not alredy utf-8
    string - string to check
    """
    try:
        return string.encode('utf-8', 'ignore')
    except:
        return str(string)

def IsEmbedded():
    try:
        return mc.IsEmbedded()
    except:
        return False

class StructLib:
    '''The recursive class for building and representing objects with.'''
    def __init__(self, obj):
        for k, v in obj.iteritems():
            if isinstance(v, dict):
                setattr(self, k, StructLib(v))
            else:
                setattr(self, k, v)
        
    def __getitem__(self, val):
        return self.__dict__[val]

    def __repr__(self):
        return '{%s}' % str(', '.join('%s : %s' % (k, repr(v)) for (k, v) in self.__dict__.iteritems()))



class storage:
    """
    Saves data to disk or persistant storage
    """

    def __init__(self, eol = 86400):
        self.path       = self.construct()
        self.eol        = eol
        self.clean()

    def construct(self):
        """sets cache dir in temp folder"""
        id     = mc.GetApp().GetId()
        prefix = "cache_"
        tmp    = mc.GetTempDir()
        path   = os.path.join(tmp, prefix + id)
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    def clean(self):
        """removes only data that has been expired (EOL)"""
        expire = time.time() - self.eol
        for item in os.listdir(self.path):
            pointer = os.path.join(self.path, item)
            if os.path.isfile(pointer):
                timestamp = os.path.getmtime(pointer)
                if timestamp <= expire:
                    os.chmod(pointer, stat.S_IWUSR)
                    os.remove(pointer)

    def empty(self, **kwargs):
        """
        removes all data from cache
        # persistent - boolean, if true empties all persistent data (optional)
        """
        for root, dirs, files in os.walk(self.path, topdown=False):
            for name in files:
                filename = os.path.join(root, name)
                os.chmod(filename, stat.S_IWUSR)
                os.remove(filename)
            for name in dirs:
                os.rmdir(os.path.join(root, name))

        if kwargs.get('persistent', False):
            mc.GetApp().GetLocalConfig().ResetAll()


    def md5(self, string):
        """returns md5 hash of string"""
        return md5(string).hexdigest()

    def get(self, id, **kwargs):
        """
        Gets data from storage
        # id         - string, unique string to identify data
        # age        - int,    if set checks if data is not older then age in seconds (optional)
        # persistent - boolean, if true it saves the data persistent                  (optional)
        """
        if kwargs.get('age'):
            age = kwargs['age']
        else:
            age = 0

        if kwargs.get('persistent', False):
            pointer = self.md5(id)
            expire  = time.time() - age

            try:
                raw       = bz2.decompress(binascii.unhexlify(mc.GetApp().GetLocalConfig().GetValue(pointer)))
                timestamp = float(mc.GetApp().GetLocalConfig().GetValue(pointer+"_timestamp"))
                if timestamp >= expire:
                    return marshal.loads(raw)
            except:
                print traceback.format_exc()
        else:
            pointer = os.path.join( self.path, self.md5(id) )
            expire  = time.time() - age

            if os.path.isfile(pointer):
                timestamp = os.path.getmtime(pointer)
                if timestamp >= expire:
                    try:
                        fp = open( pointer)
                        data = marshal.load(fp)
                        fp.close()
                        return data
                    except:
                        print traceback.format_exc()

        return False

    def set(self, id, data, **kwargs):
        """
        Saves data to storage
        # id   - string,   unique string to identify data
        # data - any type, data to cache (string, int, list, dict)
        # persistent - boolean, if true it saves the data persistent    (optional)
        """

        if kwargs.get('persistent', False):
            pointer = self.md5(id)
            try:
                raw = marshal.dumps(data)
                mc.GetApp().GetLocalConfig().SetValue(pointer, binascii.hexlify(bz2.compress(raw)))
                mc.GetApp().GetLocalConfig().SetValue(pointer+"_timestamp", str(time.time()))
                return True
            except:
                print traceback.format_exc()

        else:
            pointer = os.path.join( self.path, self.md5(id) )
            try:
                fp = open( pointer, "wb" )
                marshal.dump(data, fp)
                fp.close()
                return True
            except:
                print traceback.format_exc()

        return False


def json_loads(url, params=""):
    try:
        if not 'render=json' in url:
            if not '?' in url:
                url += '?' + params
            else:
                url += '&'+params
        data = urlopen(url)
        jdata = StructLib( json.loads(data) )
        if jdata.head.status == "200":
            return jdata
        else:
            print jdata.head.fault
            return {}
    except:
        traceback.print_exc()
        return {}


### Sort list of dicts based on key
def sort_dict(list, key, arg=False):
    return sorted(list, key=itemgetter(key), reverse=arg)

### Sort list of instances based on attribute
def sort_instance(list, key, arg=False):
    return sorted(list, key=attrgetter(key), reverse=arg)

### return unique values from list
def unique(inlist):
    uniques = []
    for item in inlist:
        if item not in uniques:
            uniques.append(item)
    return uniques

### Get sublist from list of dicts based on keys
def select_sublist(list_of_dicts, **kwargs):
    return [dict(d) for d in list_of_dicts
            if all(d.get(k)==kwargs[k] for k in kwargs)]

def getMIME(ext):
    lib = {
        'mp2': 'audio/mpeg',
        'mp3':'audio/mpeg',
        'mpga':'audio/mpeg',
        'aif':	'audio/x-aiff',
        'm3u':	'audio/x-mpegur',
        'm4a':	'audio/mp4a-latm',
        'm4b':	'audio/mp4a-latm',
        'm4p':	'audio/mp4a-latm',
        'ra':	'audio/x-pn-realaudia',
        'ram':	'audio/x-pn-realaudiog',
        'wav':	'audio/x-wav',
        'rtmp':	'application/x-shockwave-flash',
        'flash': 'application/x-shockwave-flash',
        'asf': 'video/x-ms-asf',
        'asx': 'video/x-ms-asf',
        'wma': 'video/x-ms-asf',
        'wax': 'audio/x-ms-wax',
        'wmv': 'audio/x-ms-wmv',
        'wvx': 'video/x-ms-wvx',
        'wm': 'video/x-ms-wm',
        'wmx': 'video/x-ms-wmx', 
        }
    if ext in lib.keys():
        return lib[ext]
    else:
        return ''