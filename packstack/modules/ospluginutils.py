
import logging
import os
import re

from packstack.installer import basedefs
from packstack.installer.setup_controller import Controller
from packstack.installer.exceptions import PackStackError

controller = Controller()

PUPPET_DIR = os.path.join(basedefs.DIR_PROJECT_DIR, "puppet")
PUPPET_TEMPLATE_DIR = os.path.join(PUPPET_DIR, "templates")


class NovaConfig(object):
    """
    Helper class to create puppet manifest entries for nova_config
    """
    def __init__(self):
        self.options = {}

    def addOption(self, n, v):
        self.options[n] = v

    def getManifestEntry(self):
        entry = ""
        if not self.options:
            return entry

        entry += "nova_config{\n"
        for k, v in self.options.items():
            entry += '    "%s": value => "%s";\n' % (k, v)
        entry += "}"
        return entry


class ManifestFiles(object):
    def __init__(self):
        self.filelist = []
        self.data = {}
        self.global_data = None

    # continuous manifest file that have the same marker can be
    # installed in parallel, if on different servers
    def addFile(self, filename, marker, data=''):
        self.data[filename] = self.data.get(filename, '') + '\n' + data
        for f, p in self.filelist:
            if f == filename:
                return

        self.filelist.append((filename, marker))

    def getFiles(self):
        return [f for f in self.filelist]

    def writeManifests(self):
        """
        Write out the manifest data to disk, this should only be called once
        write before the puppet manifests are copied to the various servers
        """
        if not self.global_data:
            with open(os.path.join(PUPPET_TEMPLATE_DIR, "global.pp")) as gfp:
                self.global_data = gfp.read() % controller.CONF
        os.mkdir(basedefs.PUPPET_MANIFEST_DIR, 0700)
        for fname, data in self.data.items():
            path = os.path.join(basedefs.PUPPET_MANIFEST_DIR, fname)
            fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0600)
            with os.fdopen(fd, 'w') as fp:
                fp.write(self.global_data + data)
manifestfiles = ManifestFiles()


def getManifestTemplate(template_name):
    with open(os.path.join(PUPPET_TEMPLATE_DIR, template_name)) as fp:
        return fp.read() % controller.CONF


def appendManifestFile(manifest_name, data, marker=''):
    manifestfiles.addFile(manifest_name, marker, data)


def gethostlist(CONF):
    hosts = []
    for key, value in CONF.items():
        if key.endswith("_HOST"):
            value = value.split('/')[0]
            if value and value not in hosts:
                hosts.append(value)
        if key.endswith("_HOSTS"):
            for host in value.split(","):
                host = host.strip()
                host = host.split('/')[0]
                if host and host not in hosts:
                    hosts.append(host)
    return hosts
