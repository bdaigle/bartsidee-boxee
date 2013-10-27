from default import *
from tools import *

import time
import binascii

class BARTSIDEE_MODULE:
    def __init__(self, app):
        self.app = app

    def _List(self, module):
        #Notification
        self.app.wait.show(module)

        #Execute List function of module
        if self.app.get('debug'):
            result = self.List()
        else:
            try:
                result = self.List()
            except:
                print '%s: Error - Failed "List" function for module: %s' % (APPID, module)
                result = False

        #Check for results
        if not result:
            return False

        #Generate timestamp
        period = getattr(self, 'cachetime', 7200)
        timestamp = time.time() + period

        #Clear old module values
        for r in (r for r in self.app.searchdb if r['module'] == module ):
            self.app.searchdb.delete(r)

        #Parse information to database
        for stream in result:
            label = encodeUTF8(stream.name)

            search_item         = CreateSearch()
            search_item.module  = module
            search_item.type    = self.type
            search_item.name    = self.name
            search_item.id      = encodeUTF8(stream.id)
            search_item.episode = encodeUTF8(stream.episode)

            self.app.searchdb.insert(module=module, id=label, timestamp=timestamp, data=search_item)

        #Save database
        self.app.searchdb.commit()
        print '%s: Module "%s" loaded in the database.' % (APPID, module)

    def _Episode(self, module, stream_name, stream_id, page=1, totalpage=''):
        #Open waiting dialog
        self.app.wait.show()

        #Execute episode function of module
        if self.app.get('debug'):
            result = self.Episode(stream_name, binascii.unhexlify(stream_id), page, totalpage)
        else:
            try:
                result = self.Episode(stream_name, binascii.unhexlify(stream_id), page, totalpage)
            except:
                print '%s: Error - Failed "Episode" function for module: %s' % (APPID, module)
                result = False

        #Check for results
        if not result:
            self.app.wait.hide()
            mc.ShowDialogNotification("No episodes found for " + str(stream_name))
            return False

        #Open Episode window
        mc.ActivateWindow(14446)

        #Init list
        list = mc.GetWindow(14446).GetList(51)
        list_items = mc.ListItems()

        #Parse episode results
        for episode in result:
            list_item = mc.ListItem(mc.ListItem.MEDIA_UNKNOWN)
            list_item.SetLabel( encodeUTF8(episode.name) )

            if not episode.thumbnails:
                list_item.SetThumbnail('nothumb.png')
            else:
                list_item.SetThumbnail( str(episode.thumbnails) )

            list_item.SetProperty('icon',        str(self.app.modules.info[module]['path'] + module + '.png'))
            list_item.SetProperty('stream_id',   str(stream_id))
            list_item.SetProperty('stream_url',  str(binascii.hexlify(episode.id)))
            list_item.SetProperty('module_name', str(self.app.modules.objects[module].name))
            list_item.SetProperty('date',        encodeUTF8(episode.date))
            list_item.SetProperty('episode',     encodeUTF8(episode.episode))
            list_item.SetProperty('desc',        encodeUTF8(episode.description))
            list_item.SetProperty('module',      str(module))
            list_item.SetProperty('page',        str(episode.page))
            list_item.SetProperty('totalpage',   str(episode.totalpage))
            list_items.append(list_item)

        print "%s: Fetching episodes for '%s' page %s from %s compleet." % ( APPID, str(stream_name), str(page), str(totalpage) )

        #Stop dialog wait
        self.app.wait.hide()

        #Commit list to window 
        list.SetItems(list_items)
    


    def _Genre(self, module, genre, filter='', page=1, totalpage=''):
        #Open waiting dialog
        self.app.wait.show()

        #Execute episode function of module
        if self.app.get('debug'):
            result = self.Genre(genre, filter, page, totalpage)
        else:
            try:
                result = self.Genre(genre, filter, page, totalpage)
            except:
                print 'A "Genre Load" error occured for the module: ' + str(module)
                result = False

        #Check for results
        if not result:
            return False

        #Init list
        list = mc.GetWindow(14445).GetList(53)
        list_items = mc.ListItems()

        for item in result:
            list_item = mc.ListItem(mc.ListItem.MEDIA_UNKNOWN)
            list_item.SetLabel(encodeUTF8(item.name))
            list_item.SetThumbnail(str(item.thumbnails))
            list_item.SetProperty('icon',        str(self.app.modules.info[module]['path'] + module + '.png'))
            list_item.SetProperty('stream_id',   str(binascii.hexlify(item.id)))
            list_item.SetProperty('module_name', str(self.name))
            list_item.SetProperty('date',        str(item.date))
            list_item.SetProperty('desc',        encodeUTF8(item.description))
            list_item.SetProperty('filter',      str(item.filter))
            list_item.SetProperty('module',      str(module))
            list_item.SetProperty('episode',     str(item.episode))
            list_item.SetProperty('genre',       str(genre))
            list_item.SetProperty('page',        str(item.page))
            list_item.SetProperty('totalpage',   str(item.totalpage))
            list_items.append(list_item)

        print "%s: Fetching genre for '%s' page %s from %s compleet" % ( APPID, str(genre), str(page), str(totalpage) )
        
        #Stop dialog wait
        self.app.wait.hide()

        #Commit list to window
        list.SetItems(list_items)


    def _Play(self, module, stream_name, stream_id):
        #Stop dialog wait
        self.app.wait.show()

        #Execute episode function of module
        if self.app.get('debug'):
            result = self.Play(stream_name, binascii.unhexlify(stream_id), self.app.get('subtitle') )
        else:
            try:
                result = self.Play(stream_name, binascii.unhexlify(stream_id), self.app.get('subtitle'))
            except:
                result = False

        #Check for results
        if not result:
            self.app.wait.hide()
            return False

        #Check if result contains path
        if str(result.path) == '' and str(result.rtmpdomain) == '':
            self.app.wait.hide()
            return False

        if result.content_type:
            content_type = result.content_type
        elif self.content_type:
            content_type = self.content_type
        else:
            content_type = None

        player = mc.GetPlayer()
        if content_type == "video/x-flv":
            list_item = mc.ListItem(mc.ListItem.MEDIA_VIDEO_CLIP)
            if result.rtmpdomain:
                list_item.SetPath(str(result.rtmpdomain))
                list_item.SetProperty("PageURL",   str(result.rtmpdomain))
                list_item.SetProperty("PlayPath",  str(result.rtmpurl))
                list_item.SetProperty("TcUrl",     str(result.rtmpauth))
                list_item.SetProperty("SWFPlayer", str(result.rtmpswf))

            else:
                if not result.jsactions:
                    path = 'flash://' + str(result.domain) + '/src=' + str(result.path)
                else:
                    path = 'flash://' + str(result.domain) + '/src=' + str(result.path) + '&bx-jsactions=' + str(result.jsactions)
                list_item.SetPath(str(path))

            list_item.SetLabel(str(stream_name))
            list_item.SetTitle(str(stream_name))
            list_item.SetProviderSource(str(module))
            list_item.SetReportToServer(False)
            list_item.SetAddToHistory(False)

        else:
            list_item = mc.ListItem(mc.ListItem.MEDIA_VIDEO_CLIP)
            list_item.SetLabel(str(stream_name))
            list_item.SetTitle(str(stream_name))
            list_item.SetPath(str(result.path))
            list_item.SetProviderSource(str(module))
            list_item.SetReportToServer(False)
            list_item.SetAddToHistory(False)
            if content_type:
                list_item.SetContentType(str(content_type))

        print "%s: Playback started for '%s' from module: %s" % ( APPID, str(stream_name), str(module) )

        #Stop dialog wait
        self.app.wait.hide()

        #Start playback
        player.Play(list_item)

        if self.app.get('subtitle') and result.subtitle:
            import xbmc
            if result.subtitle_type == 'sami':
                result.subtitle = ConvertSami(result.subtitle)
            elif result.subtitle_type == 'flashxml':
                result.subtitle = ConvertFlashXML(result.subtitle)
            xbmc.sleep(5)
            xbmc.Player().setSubtitles( str(result.subtitle))
            print "%s: Subtitle added for '%s'" % ( APPID, str(stream_name) )

#===============================================================================
# Variable Objects
#===============================================================================
def CreateList():
    dict = {
        'name': '',
        'id':'',
        'episode':'',
    }
    return StructLib(dict)

def CreateSearch():
    dict = {
        'module': {},
        'type':'',
        'name':'',
        'id':'',
        'label':'',
        'episode':'',
    }
    return StructLib(dict)

def CreateEpisode():
    dict = {
        'name': '',
        'id':'',
        'description':'',
        'thumbnails':'',
        'date':'',
        'filter':'',
        'page':'',
        'totalpage':'',
        'episode':'',
    }
    return StructLib(dict)

def CreatePlay():
    dict = {
        'path': '',
        'subtitle':'',
        'subtitle_type':'',
        'domain':'',
        'jsactions':'',
        'content_type':'',
        'rtmpurl':'',
        'rtmpdomain':'',
        'rtmpauth':'',
        'rtmpswf':'',
    }
    return StructLib(dict)