from default import *

import os
import mc
import xbmc

import unicodedata
import time
import stat
import traceback
import binascii
import zlib

try:    from hashlib import md5
except: from md5 import md5
import marshal

def urlopen(app, url, params={}):
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
    http.SetUserAgent("Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.2.13) Gecko/20101206 Ubuntu/10.10 (maverick) Firefox/3.6.13")
    http.SetHttpHeader('Accept', 'text/javascript, text/html, application/xml, text/xml, */*')

    if params.get('cache', False):
        data = app.cache.get(url, age=params['cache'])
    else:
        data = app.cache.get(url)
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

    if params.get('cache', False):
        app.cache.set(url, data)

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


def ConvertSami(samiurl):
    """
    Get SAMI subtitle from string and converts it a tmp srt file, returning the path
    data - string containing sami subtitle data
    """
    from BeautifulSoup import BeautifulSoup
    data = FetchUrl(samiurl, 0)
    soup = BeautifulSoup(data, convertEntities="xml", smartQuotesTo="xml")
    i = 1
    sync = ''
    temp = ''
    for info in soup.findAll("sync"):
        if info.find(attrs={"class" : "ENUSCC"}):
            sync += str(i) + '\n'
            temp = info.find(attrs={"class" : "ENUSCC"}).contents[0]
            timemsec = str(info['start'])[-3:]
            timesec = int(str(info['start']))/1000
            hour = timesec / 3600
            minute = (timesec - (hour*3600)) / 60
            sec = timesec - (hour*3600) - (minute*60)
            srttime = str(hour) + ':' + str(minute) + ':' + str(sec) + ',' + str(timemsec)
            sync += str(srttime)
            i += 1
        else:
            timemsec = str(info['start'])[-3:]
            timesec = int(str(info['start']))/1000
            hour = timesec / 3600
            minute = (timesec - (hour*3600)) / 60
            sec = timesec - (hour*3600) - (minute*60)
            srttime = str(hour) + ':' + str(minute) + ':' + str(sec) + ',' + str(timemsec)
            sync += ' --> ' + str(srttime) + '\n'
            sync += str(temp) + '\n' + '\n'
        tmpPath = mc.GetTempDir()
        subFilePath = tmpPath+os.sep+'subcache.srt'
        f = open(subFilePath, "w")
        f.write(sync)
        f.close()
    return subFilePath

def ConvertFlashXML(path):
    """
    Get SAMI subtitle from string and converts it a tmp srt file, returning the path
    data - string containing sami subtitle data
    """
    from BeautifulSoup import BeautifulSoup
    data = FetchUrl(path)
    soup = BeautifulSoup(data, convertEntities="xml", smartQuotesTo="xml")
    i = 1
    add = 1
    sync = ''
    tmp = False
    for info in soup.findAll("p"):
        sync += str(i) + '\n'

        timesec1 = str(info['begin'])
        timesec1 = timesec1.split('.')
        timesec2 = str(info['end'])
        timesec2 = timesec2.split('.')

        for tt in [timesec1,timesec2]:
            if not tmp: tmp = True
            else: tmp = False
            hour = (int(tt[0])+add) / 3600
            minute = ((int(tt[0])+add) - (hour*3600)) / 60
            sec = (int(tt[0])+add) - (hour*3600) - (minute*60)
            sync += str(hour) + ':' + str(minute) + ':' + str(sec) + ',' + str(tt[1])

            if tmp: sync += ' --> '
            else: sync += '\n'

        sync += ConvertASCII(info.renderContents()).replace('\n','').replace('\t','').replace('<br />','\n')
        sync += '\n' + '\n'
        i += 1

    tmpPath = mc.GetTempDir()
    subFilePath = tmpPath+os.sep+'subcache.srt'
    f = open(subFilePath, "w")
    f.write(sync)
    f.close()
    return subFilePath

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
        try:
            expire = time.time() - self.eol
            for item in os.listdir(self.path):
                pointer = os.path.join(self.path, item)
                if os.path.isfile(pointer):
                    timestamp = os.path.getmtime(pointer)
                    if timestamp <= expire:
                        os.chmod(pointer, stat.S_IWUSR)
                        os.remove(pointer)
        except:
            print traceback.format_exc()

    def empty(self, **kwargs):
        """
        removes all data from cache
        # persistent - boolean, if true empties all persistent data (optional)
        """
        try:
            for root, dirs, files in os.walk(self.path, topdown=False):
                for name in files:
                    filename = os.path.join(root, name)
                    os.chmod(filename, stat.S_IWUSR)
                    os.remove(filename)
                for name in dirs:
                    os.rmdir(os.path.join(root, name))

            if kwargs.get('persistent', False):
                mc.GetApp().GetLocalConfig().ResetAll()
        except:
            print traceback.format_exc()

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
        try:
            
            if kwargs.get('persistent', False):
                pointer = self.md5(id)
                expire  = time.time() - age
                raw       = zlib.decompress(binascii.unhexlify(mc.GetApp().GetLocalConfig().GetValue(pointer)))
                timestamp = float(mc.GetApp().GetLocalConfig().GetValue(pointer+"_timestamp"))
                if timestamp >= expire:
                    return marshal.loads(raw)
            else:
                pointer = os.path.join( self.path, self.md5(id) )
                expire  = time.time() - age

                if os.path.isfile(pointer):
                    timestamp = os.path.getmtime(pointer)
                    if timestamp >= expire:
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

        try:
            if kwargs.get('persistent', False):
                pointer = self.md5(id)
                raw = marshal.dumps(data)
                mc.GetApp().GetLocalConfig().SetValue(pointer, binascii.hexlify(zlib.compress(raw)))
                mc.GetApp().GetLocalConfig().SetValue(pointer+"_timestamp", str(time.time()))
                return True

            else:
                pointer = os.path.join( self.path, self.md5(id) )
                fp = open( pointer, "wb" )
                marshal.dump(data, fp)
                fp.close()
                return True
            
        except:
            print traceback.format_exc()

        return False


class wait:
    def __init__(self):
        self.id     = 15000

    def show(self, string=None):
        try:
            label = mc.GetWindow(self.id).GetLabel(300)
        except:
            mc.ActivateWindow(self.id)
            label = mc.GetWindow(self.id).GetLabel(300)
        if string:
            label.SetLabel(encodeUTF8(string))
            
    def hide(self):
        xbmc.executebuiltin("Dialog.Close(" + str(self.id) + ")")