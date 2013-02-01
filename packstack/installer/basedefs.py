"""
provides all the predefined variables for engine-setup
"""
import os
import sys
import datetime
import tempfile

APP_NAME = "Installer"

FILE_YUM_VERSION_LOCK = "/etc/yum/pluginconf.d/versionlock.list"

_tmpdirprefix = datetime.datetime.now().strftime('%Y%m%d-%H%M%S-')

PACKSTACK_VAR_DIR = "/var/tmp/packstack"
try:
    os.mkdir(PACKSTACK_VAR_DIR, 0700)
except:
    pass

VAR_DIR = tempfile.mkdtemp(prefix = _tmpdirprefix, dir = PACKSTACK_VAR_DIR)
DIR_LOG = VAR_DIR
PUPPET_MANIFEST_DIR = os.path.join(VAR_DIR, "manifests")

FILE_INSTALLER_LOG = "setup.log"

DIR_PROJECT_DIR = os.environ.get('INSTALLER_PROJECT_DIR', os.path.join(os.path.split(sys.argv[0])[0], 'sample-project'))
DIR_PLUGINS = os.path.join(DIR_PROJECT_DIR, "plugins")
DIR_MODULES = os.path.join(DIR_PROJECT_DIR, "modules")

EXEC_RPM = "rpm"
EXEC_SEMANAGE = "semanage"
EXEC_NSLOOKUP = "nslookup"
EXEC_CHKCONFIG = "chkconfig"
EXEC_SERVICE = "service"
EXEC_IP = "ip"

#text colors
RED = "\033[0;31m"
GREEN = "\033[92m"
BLUE = "\033[94m"
YELLOW = "\033[93m"
NO_COLOR = "\033[0m"

COLORS = (RED, GREEN, BLUE, YELLOW, NO_COLOR)

#space len size for color print
SPACE_LEN = 70

RPM_LOCK_LIST = """
"""
