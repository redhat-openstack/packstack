
import os

from packstack.installer import basedefs
from packstack.installer.setup_controller import Controller

controller = Controller()

PUPPET_DIR = os.path.join(basedefs.DIR_PROJECT_DIR, "puppet")
PUPPET_TEMPLATE_DIR = os.path.join(PUPPET_DIR, "templates")

class NovaConfig(object):
    """ 
    Helper class to create puppet manifest entries for nova_config
    """
    options = {}
    def addOption(self, n, v):
        self.options[n] = v

    def getManifestEntry(self):
        entry = ""
        if not self.options:
            return entry

        entry += "nova_config{\n"
        for k,v in self.options.items():
            entry += '    "%s": value => "%s";\n'%(k,v)
        entry += "}"
        return entry

class ManifestFiles(object):
    def __init__(self):
        self.filelist = []

    # continuous manifest file that have the same marker can be 
    # installed in parallel, if on different servers
    def addFile(self, filename, marker):
        for f,p in self.filelist:
            if f == filename:
                return
        self.filelist.append((filename, marker,))

    def getFiles(self):
        return [f for f in self.filelist]
manifestfiles = ManifestFiles()

def getManifestTemplate(template_name):
    with open(os.path.join(PUPPET_TEMPLATE_DIR, template_name)) as fp:
        return fp.read()%controller.CONF

def appendManifestFile(manifest_name, data, marker=''):
    if not os.path.exists(basedefs.PUPPET_MANIFEST_DIR):
        os.mkdir(basedefs.PUPPET_MANIFEST_DIR)
    manifestfile = os.path.join(basedefs.PUPPET_MANIFEST_DIR, manifest_name)
    manifestfiles.addFile(manifestfile, marker)
    with open(manifestfile, 'a') as fp:
        fp.write("\n")
        fp.write(data)
   
def gethostlist(CONF):
    hosts = []
    for key,value in CONF.items():
        if key.endswith("_HOST"):
            value = value.split('/')[0]
            if value not in hosts:
                hosts.append(value)
        if key.endswith("_HOSTS"):
            for host in value.split(","):
                host = host.strip()
                host = host.split('/')[0]
                if host not in hosts:
                    hosts.append(host)
    return hosts
