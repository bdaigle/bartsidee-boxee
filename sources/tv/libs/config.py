from default import *
import tools

from PyDbLite import Base
import traceback
import simple_json as json


class BARTSIDEE_CONFIG:
    def __init__(self):
        self.path_temp    = mc.GetTempDir()
        self.path_module  = os.path.join( CWD, 'modules' )

        if not os.path.exists(self.path_module):
            os.makedirs(self.path_module)

        sys.path.append(self.path_module)

        self.app_version = VERSION
        self.db_version  = 11

        self.initDB()
        
        GA.debug = self.get('debug')

    def initDB(self):
        self.db = Base('maindb')
        self.db.create('id', 'data', mode = 'open')

        self.searchdb = Base('searchdb')
        self.searchdb.create('module', 'id', 'timestamp' , 'data', mode = 'open')

        self.cache = tools.storage()

        try:
            if len(self.db) < 3:
                self.default()
        except:
            self.default()
        
        records = self.db(id = 'version')
        if records[0]['data'] < self.db_version:
            self.default()

    def get(self, key):
        records = self.db(id = key)
        if records:
            return records[0]['data']
        else:
            return False

    def set(self, key, data):
        records = self.db(id = key)
        if records:
            self.db.update(records,data=data)
        else:
            self.db.insert(id=key,data=data)
        self.db.commit()

    def default(self):
        self.clearDB()
        try:
            pointer = os.path.join( CWD, 'settings.json' )
            file = open(pointer, 'r')
            defaults = json.load(file)
            file.close()
        except:
            print traceback.format_exc()
            defaults = {}
            
        for key in defaults.keys():
            self.db.insert(str(key), defaults[key])
        self.db.insert('version', self.db_version)
        self.db.commit()

    def clearDB(self):
        try:
            records = self.db()
            self.db.delete(records)
        except:
            self.db.create('id', 'data', mode="override")
        self.db.commit()

    def clearCache(self):
        self.cache.empty()

    def clearSearch(self):
        try:
            records = self.searchdb()
            self.searchdb.delete(records)
        except:
            self.searchdb.create('module', 'id', 'timestamp' , 'data', mode = 'override')
        self.searchdb.commit()

    def clearAll(self):
        self.default()
        self.clearCache()
        self.clearSearch()
