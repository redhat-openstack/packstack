"""
Installs and configures MySQL
"""

import uuid
import logging

from packstack.installer import validators
from packstack.installer import utils

from packstack.modules.ospluginutils import getManifestTemplate, appendManifestFile

# Controller object will be initialized from main flow
controller = None

# Plugin name
PLUGIN_NAME = "OS-MySQL"
PLUGIN_NAME_COLORED = utils.color_text(PLUGIN_NAME, 'blue')

logging.debug("plugin %s loaded", __name__)

def initConfig(controllerObject):
    global controller
    controller = controllerObject
    logging.debug("Adding MySQL OpenStack configuration")
    paramsList = [
                  {"CMD_OPTION"      : "mysql-host",
                   "USAGE"           : "The IP address of the server on which to install MySQL",
                   "PROMPT"          : "Enter the IP address of the MySQL server",
                   "OPTION_LIST"     : [],
                   "VALIDATORS"      : [validators.validate_ssh],
                   "DEFAULT_VALUE"   : utils.get_localhost_ip(),
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_MYSQL_HOST",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "mysql-user",
                   "USAGE"           : "Username for the MySQL admin user",
                   "PROMPT"          : "Enter the username for the MySQL admin user",
                   "OPTION_LIST"     : [],
                   "VALIDATORS"      : [validators.validate_not_empty],
                   "DEFAULT_VALUE"   : "root",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": False,
                   "CONF_NAME"       : "CONFIG_MYSQL_USER",
                   "USE_DEFAULT"     : True,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "mysql-pw",
                   "USAGE"           : "Password for the MySQL admin user",
                   "PROMPT"          : "Enter the password for the MySQL admin user",
                   "OPTION_LIST"     : [],
                   "VALIDATORS"      : [validators.validate_not_empty],
                   "DEFAULT_VALUE"   : uuid.uuid4().hex[:16],
                   "MASK_INPUT"      : True,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_MYSQL_PW",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : True,
                   "CONDITION"       : False },
                 ]

    groupDict = { "GROUP_NAME"            : "MYSQL",
                  "DESCRIPTION"           : "MySQL Config parameters",
                  "PRE_CONDITION"         : lambda x: 'yes',
                  "PRE_CONDITION_MATCH"   : "yes",
                  "POST_CONDITION"        : False,
                  "POST_CONDITION_MATCH"  : True}

    controller.addGroup(groupDict, paramsList)


def initSequences(controller):
    mysqlsteps = [
             {'title': 'Adding MySQL manifest entries',
              'functions':[createmanifest]}
    ]
    controller.addSequence("Installing MySQL", [], [], mysqlsteps)


def createmanifest(config):
    if config['CONFIG_MYSQL_INSTALL'] == 'y':
        install = True
        suffix = 'install'
    else:
        install = False
        suffix = 'noinstall'

    # In case we are not installing MySQL server, mysql* manifests have
    # to be run from Keystone host
    host = install and config['CONFIG_MYSQL_HOST'] \
                    or config['CONFIG_KEYSTONE_HOST']
    manifestfile = "%s_mysql.pp" % host
    manifestdata = [getManifestTemplate('mysql_%s.pp' % suffix)]

    def append_for(module, suffix):
        # Modules have to be appended to the existing mysql.pp
        # otherwise pp will fail for some of them saying that
        # Mysql::Config definition is missing.
        template = "mysql_%s_%s.pp" % (module, suffix)
        manifestdata.append(getManifestTemplate(template))

    append_for("keystone", suffix)
    hosts = set()
    for mod in ['nova', 'cinder', 'glance', 'neutron', 'heat']:
        if config['CONFIG_%s_INSTALL' % mod.upper()] == 'y':
            append_for(mod, suffix)
            # Check wich modules are enabled so we can allow their
            # hosts on the firewall
            if mod != 'nova' and mod != 'neutron':
                hosts.add(config.get('CONFIG_%s_HOST' % mod.upper()).strip())
            elif mod == 'neutron':
                hosts.add(config.get('CONFIG_NEUTRON_SERVER_HOST').strip())
            elif config['CONFIG_NOVA_INSTALL'] != 'n':
                #In that remote case that we have lot's of nova hosts
                hosts.add(config.get('CONFIG_NOVA_API_HOST').strip())
                hosts.add(config.get('CONFIG_NOVA_CERT_HOST').strip())
                hosts.add(config.get('CONFIG_NOVA_VNCPROXY_HOST').strip())
                hosts.add(config.get('CONFIG_NOVA_CONDUCTOR_HOST').strip())
                hosts.add(config.get('CONFIG_NOVA_SCHED_HOST').strip())
                if config['CONFIG_NEUTRON_INSTALL'] != 'y':
                    dbhosts = split_hosts(config['CONFIG_NOVA_NETWORK_HOSTS'])
                    hosts |= dbhosts
                for host in config.get('CONFIG_NOVA_COMPUTE_HOSTS').split(','):
                    hosts.add(host.strip())

    config['FIREWALL_ALLOWED'] = ",".join(["'%s'" % i for i in hosts])
    config['FIREWALL_SERVICE_NAME'] = "mysql"
    config['FIREWALL_PORTS'] = "'3306'"
    manifestdata.append(getManifestTemplate("firewall.pp"))

    appendManifestFile(manifestfile, "\n".join(manifestdata), 'pre')
