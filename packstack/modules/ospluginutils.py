
import os

from packstack.installer import basedefs
from packstack.installer.setup_controller import Controller

controller = Controller()

PUPPET_DIR = os.path.join(basedefs.DIR_PROJECT_DIR, "puppet")
PUPPET_MANIFEST_DIR = os.path.join(PUPPET_DIR, "manifests")
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

def getManifestTemplate(template_name):
    with open(os.path.join(PUPPET_TEMPLATE_DIR, template_name)) as fp:
        return fp.read()%controller.CONF

def appendManifestFile(manifest_name, data):
    manifestfile = os.path.join(PUPPET_MANIFEST_DIR, manifest_name)
    if manifestfile not in controller.CONF['CONFIG_MANIFESTFILES']:
        controller.CONF['CONFIG_MANIFESTFILES'].append(manifestfile)
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

                                         
