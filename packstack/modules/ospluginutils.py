
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

    # continuous manifest file that have the same marker can be
    # installed in parallel, if on different servers
    def addFile(self, filename, marker):
        for f, p in self.filelist:
            if f == filename:
                return
        self.filelist.append((filename, marker,))

    def getFiles(self):
        return [f for f in self.filelist]
manifestfiles = ManifestFiles()


def getManifestTemplate(template_name):
    with open(os.path.join(PUPPET_TEMPLATE_DIR, template_name)) as fp:
        return fp.read() % controller.CONF


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
    for key, value in CONF.items():
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


_error_exceptions = [
    # puppet preloads a provider using the mysql command before it is installed
    re.compile('Command mysql is missing'),
    # puppet preloads a database_grant provider which fails if /root/.my.cnf
    # this is ok because it will be retried later if needed
    re.compile('Could not prefetch database_grant provider.*?\\.my\\.cnf'),
    # swift puppet module tries to install swift-plugin-s3, there is no such
    # pakage on RHEL, fixed in the upstream puppet module
    re.compile('yum.*?install swift-plugin-s3'),
]


def isErrorException(line):
    for ee in _error_exceptions:
        if ee.search(line):
            return True
    return False


_re_color = re.compile('\x1b.*?\d\dm')
_re_errorline = re.compile('err: | Syntax error at|^Duplicate definition:|'
                           '^No matching value for selector param|'
                           '^Parameter name failed:|Error: ')


def validate_puppet_logfile(logfile):
    """
    Check a puppet log file for errors and raise an error if we find any
    """
    fp = open(logfile)
    data = fp.read()
    fp.close()
    manifestfile = os.path.splitext(logfile)[0]
    for line in data.split('\n'):
        line = line.strip()

        if _re_errorline.search(line) is None:
            continue

        message = _re_color.sub('', line)  # remove colors
        if isErrorException(line):
            logging.info("Ignoring expected error during puppet run %s : %s" %
                (manifestfile, message))
            continue

        message = "Error during puppet run : " + message
        logging.error("Error  during remote puppet apply of " + manifestfile)
        logging.error(data)
        raise PackStackError(message)
