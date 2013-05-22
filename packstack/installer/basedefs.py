# -*- coding: utf-8 -*-

"""
This module provides all the predefined variables.
"""

import os
import sys
import datetime
import tempfile


APP_NAME = "Installer"

FILE_YUM_VERSION_LOCK = "/etc/yum/pluginconf.d/versionlock.list"

PACKSTACK_VAR_DIR = "/var/tmp/packstack"
try:
    os.mkdir(PACKSTACK_VAR_DIR, 0700)
except:
    pass

_tmpdirprefix = datetime.datetime.now().strftime('%Y%m%d-%H%M%S-')
VAR_DIR = tempfile.mkdtemp(prefix=_tmpdirprefix, dir=PACKSTACK_VAR_DIR)
DIR_LOG = VAR_DIR
PUPPET_MANIFEST_RELATIVE = "manifests"
PUPPET_MANIFEST_DIR = os.path.join(VAR_DIR, PUPPET_MANIFEST_RELATIVE)

FILE_INSTALLER_LOG = "setup.log"

DIR_PROJECT_DIR = os.environ.get('INSTALLER_PROJECT_DIR', os.path.join(os.getcwd(), 'packstack'))
DIR_PLUGINS = os.path.join(DIR_PROJECT_DIR, "plugins")
DIR_MODULES = os.path.join(DIR_PROJECT_DIR, "modules")



EXEC_RPM = "rpm"
EXEC_SEMANAGE = "semanage"
EXEC_NSLOOKUP = "nslookup"
EXEC_CHKCONFIG = "chkconfig"
EXEC_SERVICE = "service"
EXEC_IP = "ip"

# space len size for color print
SPACE_LEN = 70
