from default import *
from modules import *
from tools import *
from config import *
from search import *

import binascii
import traceback

from operator import itemgetter

class BARTSIDEE_MAIN(BARTSIDEE_CONFIG):
    ### Init main app
    def __init__(self):
        BARTSIDEE_CONFIG.__init__(self)
        self.wait    = wait()

        self.wait.show()

        self.modules = BARTSIDEE_MODULES(self)
        self.search  = BARTSIDEE_SEARCH(self)
        
        self.wait.hide()

    ### GUI Modules window
    def Modules(self):
        list = mc.GetWindow(14444).GetList(52)
        list_items = mc.ListItems()

        for module in self.modules.info.keys():
            if module in self.get('modules'):
                list_item = mc.ListItem(mc.ListItem.MEDIA_UNKNOWN)
                list_item.SetLabel( str( module ) )
                list_item.SetThumbnail( str( self.modules.info[module]['path'] + module + '.png' ) )
                list_items.append(list_item)
        list.SetItems(list_items)

    ### GUI Settings window
    def Settings(self):
        online_data = self.modules.modules_online

        list = mc.GetWindow(14444).GetList(53)
        list_items = mc.ListItems()

        for module in online_data.keys():
            list_item = mc.ListItem(mc.ListItem.MEDIA_UNKNOWN)
            list_item.SetLabel(str(module))
            if self.get('local'):
                list_item.SetProperty('country', str("LC"))
            else:
                list_item.SetProperty('country', str( online_data[module]['country'] ))
            list_item.SetProperty('description', str( online_data[module]['description'] ))
            list_item.SetProperty('logo', str( self.modules.modules_online[module]['path'] + module + '.png') )
            if module in self.get('modules'):
                list_item.SetThumbnail(str('gtk-apply.png'))
            else:
                list_item.SetThumbnail(str('gtk-close.png'))
            list_items.append(list_item)
        list.SetItems(list_items)

        list = mc.GetWindow(14444).GetList(54)
        list_items = mc.ListItems()

        options = {"subtitle":"Subtitles On/Off","clear":"Reset to defaults"}
        for key in options.keys():
            list_item = mc.ListItem(mc.ListItem.MEDIA_UNKNOWN)
            list_item.SetLabel(options[key])
            list_item.SetProperty('id', key)
            list_item.SetProperty('version', str(self.app_version))
            if key == "subtitle":
                if self.get('subtitle'):
                    list_item.SetThumbnail(str('gtk-apply.png'))
                else:
                    list_item.SetThumbnail(str('gtk-close.png'))
            else:
                list_item.SetThumbnail(str('gtk-close.png'))
            list_items.append(list_item)
        list.SetItems(list_items)

    ### GUI App window
    def App(self, module):
        GA.setPageView(module)
        types = self.modules.objects[module].type

        tmp_types = ['home', 'search']
        if 'list' in types: tmp_types.append('list')
        if 'genre' in types: tmp_types.append('genre')

        mc.GetWindow(14445).ClearStateStack(False)
        mc.ActivateWindow(14445)
        list = mc.GetWindow(14445).GetList(54)
        list_items = mc.ListItems()
        for type in tmp_types:
            list_item = mc.ListItem(mc.ListItem.MEDIA_UNKNOWN)
            list_item.SetLabel(str(type))
            list_item.SetThumbnail(str( self.modules.info[module]['path'] + module + '.png') )
            list_item.SetProperty('name', str(self.modules.objects[module].name))
            list_item.SetProperty('module', str(module))
            list_items.append(list_item)
        list.SetItems(list_items)
        list.SetFocusedItem(1)

    ### GUI List window
    def List(self, module):
        list = mc.GetWindow(14445).GetList(52)
        list_items = mc.ListItems()

        try:
            results = [ (r['id'], r['data']) for r in self.searchdb if r['module'] == module]
        except:
            print traceback.format_exc()
            self.clearSearch()
            results = {}

        results.sort(key=itemgetter(0))

        for item in results:
            list_item = mc.ListItem(mc.ListItem.MEDIA_UNKNOWN)
            list_item.SetLabel(str(item[0]))
            list_item.SetProperty('icon', str( self.modules.info[module]['path'] + module + '.png') )
            list_item.SetProperty('stream_id', str(binascii.hexlify(item[1].id)))
            list_item.SetProperty('module', str(item[1].module))
            list_item.SetProperty('type', str(item[1].type))
            list_item.SetProperty('name', str(item[1].name))
            list_items.append(list_item)
        list.SetItems(list_items)

    ### GUI Genre window
    def Genre(self, module):
        genres = getattr(self.modules.objects[module], 'genre', [])
        if genres:
            list = mc.GetWindow(14445).GetList(55)
            list_items = mc.ListItems()

            for genre in genres:
                list_item = mc.ListItem(mc.ListItem.MEDIA_UNKNOWN)
                list_item.SetLabel(str(genre))
                list_item.SetProperty('module', str(module))
                list_items.append(list_item)
            list.SetItems(list_items)

        filters = genres = getattr(self.modules.objects[module], 'filters', [])
        if filters:
            list = mc.GetWindow(14445).GetList(56)
            list_items = mc.ListItems()

            filters.insert(0, 'None')
            for filter in filters:
                list_item = mc.ListItem(mc.ListItem.MEDIA_UNKNOWN)
                list_item.SetLabel(encodeUTF8(filter))
                list_items.append(list_item)
            list.SetItems(list_items)

    ### Process action
    def down(self, id):
        window = mc.GetWindow(14444)
        self.wait.show()
        
        if id == 'settings':
            list = window.GetList(53)
            listitems = list.GetItems()
            listitem = listitems[list.GetFocusedItem()]
            module = listitem.GetLabel()

            modules_enabled = self.get('modules')
            if module in modules_enabled:
                modules_enabled.remove(module)
                self.modules.load()
                self.search.remove(module)
            else:
                modules_enabled.append(module)
                self.modules.load()
                self.search.add(module)
            self.set('modules', modules_enabled)
            self.Settings()
            

        elif id == 'config':
            list = window.GetList(54)
            listitems = list.GetItems()
            listitem = listitems[list.GetFocusedItem()]
            id = listitem.GetProperty('id')
            if id == "subtitle":
                if self.get('subtitle'):
                    self.set('subtitle', False)
                else:
                    self.set('subtitle', True)
                self.Settings()
            if id == "clear":
                self.clearAll()
                self.modules.__init__(self)
                self.search.__init__(self)
                self.Settings()

        self.wait.hide()
