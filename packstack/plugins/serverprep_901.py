"""
prepare server
"""

import logging

import packstack.installer.engine_validators as validate
from packstack.installer import basedefs
import packstack.installer.common_utils as utils

from packstack.modules.ospluginutils import gethostlist

# Controller object will be initialized from main flow
controller = None

# Plugin name
PLUGIN_NAME = "OS-SERVERPREPARE"
PLUGIN_NAME_COLORED = utils.getColoredText(PLUGIN_NAME, basedefs.BLUE)

logging.debug("plugin %s loaded", __name__)

def initConfig(controllerObject):
    global controller
    controller = controllerObject
    logging.debug("Adding SERVERPREPARE KEY configuration")
    conf_params = {"SERVERPREPARE": [
                  {"CMD_OPTION"      : "use-epel",
                   "USAGE"           : "Install OpenStack from EPEL. If set to \"y\" EPEL will be installed on each server",
                   "PROMPT"          : "Should Packstack install EPEL on each server",
                   "OPTION_LIST"     : ["y", "n"],
                   "VALIDATION_FUNC" : validate.validateOptions,
                   "DEFAULT_VALUE"   : "n",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_USE_EPEL",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "additional-repo",
                   "USAGE"           : "A comma separated list of URLs to any additional yum repositories to install",
                   "PROMPT"          : "Enter a comma separated list of URLs to any additional yum repositories to install",
                   "OPTION_LIST"     : [],
                   "VALIDATION_FUNC" : lambda a,b: True,
                   "DEFAULT_VALUE"   : "",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_REPO",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "rh-username",
                   "USAGE"           : "To subscribe each server with Red Hat subscription manager, include this with CONFIG_RH_PASSWORD",
                   "PROMPT"          : "To subscribe each server to Red Hat enter a username here",
                   "OPTION_LIST"     : [],
                   "VALIDATION_FUNC" : lambda a,b: True,
                   "DEFAULT_VALUE"   : "",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_RH_USERNAME",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "rh-password",
                   "USAGE"           : "To subscribe each server with Red Hat subscription manager, include this with CONFIG_RH_USERNAME",
                   "PROMPT"          : "To subscribe each server to Red Hat enter your password here",
                   "OPTION_LIST"     : [],
                   "VALIDATION_FUNC" : lambda a,b: True,
                   "DEFAULT_VALUE"   : "",
                   "MASK_INPUT"      : True,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_RH_PASSWORD",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
            ]
        }

    conf_groups = [
            { "GROUP_NAME"            : "SERVERPREPARE",
              "DESCRIPTION"           : "Server Prepare Configs ",
              "PRE_CONDITION"         : utils.returnYes,
              "PRE_CONDITION_MATCH"   : "yes",
              "POST_CONDITION"        : False,
              "POST_CONDITION_MATCH"  : True},
        ]

    for group in conf_groups:
        paramList = conf_params[group["GROUP_NAME"]]
        controller.addGroup(group, paramList)

def initSequences(controller):
    preparesteps = [
             {'title': 'Preparing servers', 'functions':[serverprep]}
    ]
    controller.addSequence("Preparing servers", [], [], preparesteps)


def serverprep():
    for hostname in gethostlist(controller.CONF):
        if '/' in hostname:
            hostname = hostname.split('/')[0]
        server = utils.ScriptRunner(hostname)

        # install epel if on rhel and epel is configured
        if controller.CONF["CONFIG_USE_EPEL"] == 'y':
            server.append("export EPEL_RPM_URL=\"http://download.fedoraproject.org/pub/epel/6/"
                                                "$([ `uname -i` = 'x86_64' ] && echo 'x86_64' || echo 'i386')"
                                                "/epel-release-6-8.noarch.rpm\"")
            server.append("grep 'Red Hat Enterprise Linux' /etc/redhat-release && "
                          "( rpm -q epel-release || rpm -Uvh $EPEL_RPM_URL ) || echo -n ''")

        server.append("mkdir -p %s" % basedefs.PUPPET_MANIFEST_DIR)

        # set highest priority of RHOS repository if EPEL is installed
        server.append("rpm -q epel-release && yum install -y yum-plugin-priorities || true")
        subs_cmd = ('rpm -q epel-release && openstack-config --set %(repo_file)s %(repo)s priority %(priority)s || true')
        server.append(subs_cmd % {"repo_file": "/etc/yum.repos.d/redhat.repo",
                                  "repo": "rhel-server-ost-6-folsom-rpms",
                                  "priority": 1})

        # Add yum repositories if configured
        CONFIG_REPO = controller.CONF["CONFIG_REPO"].strip()
        if CONFIG_REPO:
            for i, url in enumerate(CONFIG_REPO.split(',')):
                reponame = 'packstack_%d' % i
                server.append('echo "[%s]\nname=%s\nbaseurl=%s\nenabled=1\npriority=1\ngpgcheck=0"'
                              ' > /etc/yum.repos.d/%s.repo' % (reponame, reponame, url, reponame))

        # Subscribe to Red Hat Repositories if configured
        RH_USERNAME = controller.CONF["CONFIG_RH_USERNAME"].strip()
        RH_PASSWORD = controller.CONF["CONFIG_RH_PASSWORD"].strip()
        if RH_USERNAME:
            server.append("subscription-manager register --username=\"%s\" --password=\"%s\" --autosubscribe || true" % (RH_USERNAME, RH_PASSWORD.replace('"','\\"')))
            server.append("subscription-manager list --consumed | grep -i openstack || "
                          "subscription-manager subscribe --pool $(subscription-manager list --available | grep -e 'Red Hat OpenStack' -m 1 -A 2 | grep 'Pool Id' | awk '{print $3}')")
            server.append("yum clean all")
            server.append("yum-config-manager --enable rhel-server-ost-6-folsom-rpms")

        server.append("yum clean metadata")
        server.execute(maskList=[controller.CONF["CONFIG_RH_PASSWORD"]])
