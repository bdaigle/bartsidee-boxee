from default import *
from tools import *

import simple_json as json
import traceback
import imp
import urllib
import workerpool
import stat

class BARTSIDEE_MODULES:
    def __init__(self, app):
        self.app     = app
        self.objects = {}
        self.info    = {}

        self.load()

    def load(self):
        """Load enabled modules"""
        #self.app.wait.show()
        local = self.app.get('local')

        #Get local modules
        self.modules_local = self.load_local_modules()

        #Get online modules
        if not local:
            self.modules_online = self.load_online_module()
        else:
            self.modules_online = self.modules_local

        #Load modules
        self.modules_enabled = self.app.get('modules')

        #Parse modules
        self.fetch(self.modules_enabled)

        #Clean directory
        if not self.app.get('local'):
            for module in self.modules_local.keys():
                try:    local = self.modules_local[module]['version']
                except: local = False
                if module not in self.modules_online.keys() or module not in self.modules_enabled:
                    self.remove(module, local)

        self.app.set('modules', self.modules_enabled)
        #self.app.wait.hide()

        print '%s: Modules loaded' % APPID

    def fetch(self, modules):
        """Multithread fetch of modules"""
        # Make a pool, five threads
        pool = workerpool.WorkerPool(size=5)

        # Perform the mapping
        pool.map(self.load_module, modules)

        # Send shutdown jobs to all threads, and wait until all the jobs have been completed
        pool.shutdown()
        pool.wait()

    def load_module(self, module):
        """Job for module loader"""
        load = True
        remove = False
        local = False
        online = False

        #Check if module is local
        if module in self.modules_local.keys():
            try:    local = self.modules_local[module]['version']
            except: pass

        #Check if module is online
        if module in self.modules_online.keys() and not self.app.get('local'):
            try:    online = self.modules_online[module]['version']
            except: pass

        #Remove module if not online
        if local and not online and not self.app.get('local'):
            del self.modules_active[module]
            remove = True
            load = False

        if local < online and local > 0 and not self.app.get('local'):
            remove = True

        if remove:
            try:
                self.remove(module, local)
                del self.modules_local[module]
            except:
                print "%s: Error when trying to remove module: %s" % (APPID, module)

        if local < online:
            path = self.modules_online[module]['path']
            self.download(path, module, online)
            local = online

        if load and local:
            if self.app.get('local'):
                online = local
            if not self.app.get('debug'):
                try:
                    self.import_module(module, online)
                except:
                    self.remove(module, online)
                    self.load()
                    return
            else:
                self.import_module(module, online)
            
            if self.app.get('local'):
                self.info[module] = self.modules_local[module]
            else:
                self.info[module] = self.modules_online[module]

    def load_online_module(self):
        """Fetch online modules"""
        repositories = self.app.get('repositories')
        data = {}
        for repo in repositories:
            path = repo['path']
            if path[-1:] == '/':
                path = repo[:-1]
            try:
                raw_json = urlopen(self.app, str(path + '/index.json'), {'cache':3600} )
                raw = json.loads(raw_json)
                modules = dict( ( module['name'] , {'version': module['version'], 'country': module['country'], 'description': module['desc'], 'path': path + '/' + module['name'] +'/'}) for module in raw['modules'] )
                data.update(modules)
            except:
                print traceback.format_exc()
        return data

    def load_local_modules(self):
        """Fetch local modules"""
        data = {}
        for dirpath, dirnames, filenames in os.walk(self.app.path_module):
            for dir in dirnames:
                if '-' in dir:
                    dirname = dir.split('-')
                else:
                    dirname = [dir,0]
                data[dirname[0]] = {"version":int(dirname[1]), "description":"", "path":self.app.path_module + os.sep + dir + os.sep}
        return data

    def remove(self, module, version):
        """Remove a module"""
        if version:
            path = os.path.join(self.app.path_module, module+'-'+str(version))
        else:
            path = os.path.join(self.app.path_module, module)

        for root, dirs, files in os.walk(path, topdown=False):
            for name in files:
                filename = os.path.join(root, name)
                os.chmod(filename, stat.S_IWUSR)
                os.remove(filename)
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(path)

    def download(self, url, name, version):
        """Download a module"""
        dir_path = os.path.join(self.app.path_module, name+'-'+str(version))

        py_path = os.path.join(dir_path, name+'.py')
        py_init = os.path.join(self.app.path_module, name+'-'+str(version), '__init__.py')
        py_url = url + name+'.py'

        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        urllib.urlretrieve(py_url, py_path)

        tmp = file(py_init, "w")
        tmp.close()

    def import_module(self, module, version):
        """import module funtion"""
        unique_name = module +'-'+str(version)
        obj = False
        try:
            obj = sys.modules[module]
        except KeyError:
            pass

        fp, pathname, description = imp.find_module(module, [os.path.join(self.app.path_module, unique_name)])

        try:
            obj = imp.load_module(module,fp, pathname, description)
        finally:
            if fp:
                fp.close()

        if obj:
            self.objects[module] = obj.Module(self.app)





