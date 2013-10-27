from default import *

import tools
import urllib
import random
import xbmc

window = mc.GetWindow(14000)
config = mc.GetApp().GetLocalConfig()

class init:
    def __init__(self):
        self.base = "http://opml.radiotime.com/"
        self.serial = self.generateID()
        self.load()

    def load(self):
        mc.ShowDialogWait()
        params = urllib.urlencode({"render":"json", "partnerId":"HyzqumNX", "serial":self.serial})
        data = tools.json_loads(self.base, params)
        if not data:
            return

        items = self.parse(data)
        list = window.GetList(60)
        list.SetItems(items)
        mc.HideDialogWait()

        self.browse(list, 0, push=False)


    def generateID(self):
        id = config.GetValue("tunein_id")
        if id:
            return id
        id = str(random.randint(1000000000000000, 9999999999999999))
        config.SetValue("tunein_id", id)
        return id

    def parse(self, data):
        empty = mc.ListItems()
        items = ""
        if hasattr(data, 'body'):
            try:    title = data.head.title
            except: title = ""
            items = self.parsetree(empty, data.body, title)
        return items

    def parsetree(self, items, data, title):
        for item in data:
            if item.get('children', False):
                items = self.parsetree(items, item['children'], title)
            else:
                r = self.parse_item(item, title)
                if r:
                    items.append(r)
        return items

    def parse_item(self, station, title):
        item = ""
        type = station['type']
        if type == "link":
            item = mc.ListItem(mc.ListItem.MEDIA_UNKNOWN)
            item.SetLabel( tools.encodeUTF8(station['text']) )
            item.SetPath( str(station['URL']) )
            item.SetProperty("icon", 'folder.png')
            item.SetProperty("type", str(station['type']) )
            item.SetProperty("title", str(title))

        if type == "audio":
            item = mc.ListItem(mc.ListItem.MEDIA_AUDIO_OTHER)
            item.SetLabel( tools.encodeUTF8(station['text']) )
            item.SetPath( str(station['URL']) )
            item.SetThumbnail(str(station['image']))
            item.SetProperty("subtext", tools.encodeUTF8(station['subtext']))
            item.SetProperty("icon", 'music.png')
            item.SetProperty("type", str(station['type'] ))
            item.SetProperty("title", str(title))
            item.SetProperty("bitrate", str(station.get('bitrate', '') ))
            item.SetProperty("reliability", str(station.get('reliability', '') ))
            item.SetReportToServer(False)
            item.SetAddToHistory(False)

        return item

    def browse(self, list, focus, **kwargs):
        mc.ShowDialogWait()
        items = list.GetItems()
        item = items[focus]

        if item.GetProperty('type') == "audio":
            self.play(item)
            return

        window.GetControl(50).SetFocus()
        params = urllib.urlencode({"render":"json"})
        data = tools.json_loads( item.GetPath(), params)
        if not data:
            return

        items = self.parse(data)
        if not items:
            return
        
        if kwargs.get('push', True):
            window.PushState()
            
        list = window.GetList(50)
        list.SetItems(items)
        mc.HideDialogWait()
        

    def search(self, q):
        params = urllib.urlencode({"render":"json", "query": q, "filter":""})
        url = self.base + "Search.ashx"
        data = tools.json_loads( url, params)
        if not data:
            return

        items = self.parse(data)
        if not items:
            return

        if kwargs.get('push', True):
            window.PushState()

        list = window.GetList(50)
        list.SetItems(items)


    def play(self, item):
        params = urllib.urlencode({"render":"json"})
        data = tools.json_loads( item.GetPath(), params )
        if not data:
            return
        
        data.body = tools.sort_dict(data.body, 'bitrate')
        mime = tools.getMIME( str(data.body[0]['media_type']) )

        item.SetPath(str(data.body[0]['url']))
        item.SetContentType( str( mime ) )
        
        player = mc.GetPlayer()
        player.Play(item)

        label = window.GetLabel(3002)
        label.SetLabel( item.GetLabel() )