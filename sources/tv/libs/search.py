from default import *
from tools import *
from library import *

import binascii
import time
from operator import itemgetter
import workerpool

class BARTSIDEE_SEARCH:
    def __init__(self, app):
        self.app = app
        self.loading = []
        #self.app.wait.show()

        #Check if any modules enabled
        if len(self.app.modules.info) < 1 :
            mc.ShowDialogNotification("You can enable modules in the settings section")

        #Clean items not active
        try:
            records = [ r for r in self.app.searchdb if r['module'] not in self.app.modules.info.keys()]
        except:
            print traceback.format_exc()
            self.app.clearSearch()
            records = {}

        if records:
            self.app.searchdb.delete(records)

        #Clean items with old cache
        try:
            records = [ r for r in self.app.searchdb if r['timestamp'] < time.time() and r['module'] in self.app.modules.info.keys()]
        except:
            print traceback.format_exc()
            self.app.clearSearch()
            records = {}
        if records:
            self.app.searchdb.delete(records)

        #Refresh non loaded modules
        loaded_modules = []
        [ loaded_modules.append(r['module']) for r in self.app.searchdb if r['module'] in self.app.modules.info.keys() and r['module'] not in loaded_modules ]
        [ self.add(module) for module in self.app.modules.info.keys() if module not in loaded_modules ]

        #self.app.wait.hide()
        print '%s: Database refreshed.' % (APPID)

    def Search(self, query, window, module=False):
        self.loading.append('true')
        mc.GetWindow(window).GetControl(1203).SetVisible(True)

        self.results = []
        search_dynamic = self.app.get('search_dynamic')

        #If general search
        if not module:
            #lookup in database
            self.results += [ (r['id'], r['data'], r['module']) for r in self.app.searchdb if query.lower() in ConvertASCII(r['id'].lower()) ]

            #lookup in online search
            self.dynamic_search(search_dynamic, query)

        #Else do a module search
        else:
            #lookup in database
            if module not in search_dynamic:
                self.results += [ (r['id'], r['data'], module) for r in self.app.searchdb if r['module'] == module and query.lower() in ConvertASCII(r['id'].lower() ) ]

            else:
                self._dynamic_search(module, query)

        #sort results
        self.results.sort(key=itemgetter(0))

        #Init window vars
        list  = mc.GetWindow(window).GetList(51)
        focus = int(list.GetFocusedItem())

        #Parse data
        list_items = mc.ListItems()
        for item in self.results:
            list_item = mc.ListItem(mc.ListItem.MEDIA_UNKNOWN)
            list_item.SetLabel(str(item[0]))
            list_item.SetProperty('icon',        str(self.app.modules.info[item[2]]['path'] + item[2] + '.png'))
            list_item.SetProperty('stream_id',   str(binascii.hexlify(item[1].id)))
            list_item.SetProperty('module',      str(item[1].module))
            list_item.SetProperty('type',        str(item[1].type))
            list_item.SetProperty('name',        str(item[1].name))
            list_item.SetProperty('episode',     str(item[1].episode))
            list_items.append(list_item)

        #Commit items to gui
        list.SetItems(list_items)

        #Correct focus position in search window
        max = len(list_items) - 1
        if focus > 0 and focus < max:
            list.SetFocusedItem(focus)
        elif focus > max:
            list.SetFocusedItem(max)

        del self.results

        self.loading.pop()
        if not self.loading:
            mc.GetWindow(window).GetControl(1203).SetVisible(False)

    def dynamic_search(self, modules, query):
        queries = 6 * [query]
        pool = workerpool.WorkerPool(size=5)
        pool.map(self._dynamic_search, modules, queries)
        pool.shutdown()
        pool.wait()

    def _dynamic_search(self, module, query):
        results = []
        if self.app.get('debug'):
            data = self.app.modules.objects[module].Search(query)
        else:
            try:
                data = self.app.modules.objects[module].Search(query)
            except:
                print '%s: "Dynamic Search" error occured for the module: %s' % ( APPID, module )
                data = False
        if data:
            for item in data:
                label              = encodeUTF8(item.name)
                search_item        = CreateSearch()
                search_item.module = module
                search_item.type   = self.app.modules.objects[module].type
                search_item.name   = self.app.modules.objects[module].name
                search_item.episode= item.episode
                search_item.id     = item.id
                results.append( (label, search_item, module) )
        self.results += results


    def add(self, module):
        type = self.app.modules.objects[module].type
        if 'search' in type:
            search_dynamic = self.app.get('search_dynamic')
            if module not in search_dynamic:
                search_dynamic.append(module)
            self.app.set('search_dynamic', search_dynamic)
        elif 'list' in type:
            self.app.modules.objects[module]._List(module)

        print '%s: Module "%s" added to the database.' % (APPID, module)

    def remove(self, module):
        records = [ r for r in self.app.searchdb if r['module'] == module]
        if records:
            self.app.searchdb.delete(records)

        search_dynamic = self.app.get('search_dynamic')
        if module in search_dynamic:
            search_dynamic.remove(module)
            self.app.set('search_dynamic', search_dynamic)

        print '%s: Module "%s" removed from the database.' % (APPID, module)

    def getHistory(self, index=0):
        data = self.app.get('search_history')[index]

    def setHistory(self, query):
        data = self.app.get('search_history')
        data.insert(0, query)
        if len(data) > 10:
            data.pop()
        self.app.set('search_history', data)