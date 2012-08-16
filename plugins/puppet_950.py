"""
Installs and configures puppet
"""
import logging
import os
import uuid

import engine_validators as validate
import basedefs
import common_utils as utils

# Controller object will be initialized from main flow
controller = None

# Plugin name
PLUGIN_NAME = "OSPUPPET"
PLUGIN_NAME_COLORED = utils.getColoredText(PLUGIN_NAME, basedefs.BLUE)

logging.debug("plugin %s loaded", __name__)

PUPPETDIR = "puppet"
MODULEDIR = os.path.join(PUPPETDIR, "modules")
MANIFESTDIR = os.path.join(PUPPETDIR, "manifests")
PUPPET_MODULES = [
    ('https://github.com/puppetlabs/puppetlabs-glance.git', 'glance'),
    ('https://github.com/puppetlabs/puppetlabs-horizon.git', 'horizon'),
    ('https://github.com/puppetlabs/puppetlabs-keystone.git', 'keystone'),
    ('https://github.com/puppetlabs/puppetlabs-nova.git', 'nova'),
    ('https://github.com/puppetlabs/puppetlabs-openstack.git', 'openstack'),
    ('https://github.com/puppetlabs/puppetlabs-horizon', 'horizon'),
    ('https://github.com/puppetlabs/puppetlabs-stdlib.git', 'stdlib'),
    ('https://github.com/puppetlabs/puppetlabs-sysctl.git', 'sysctl'),
    ('https://github.com/puppetlabs/puppetlabs-mysql.git', 'mysql'),
    ('https://github.com/puppetlabs/puppetlabs-concat.git', 'concat'),
    ('https://github.com/puppetlabs/puppetlabs-create_resources.git', 'create_resources'),
    ('https://github.com/puppetlabs/puppetlabs-firewall.git', 'firewall'),
    ('https://github.com/saz/puppet-memcached.git', 'memcached'),
    ('https://github.com/derekhiggins/puppet-qpid.git', 'qpid'),
    ('https://github.com/derekhiggins/puppet-vlan.git', 'vlan')
]

def initConfig(controllerObject):
    global controller
    controller = controllerObject
    logging.debug("Adding Openstack Puppet configuration")
    paramsList = [
                  {"CMD_OPTION"      : "remove-puppetmodules",
                   "USAGE"           : "Causes the Puppet modules to be removed (if present), and as a result re-cloned from git",
                   "PROMPT"          : "Should we remove the Puppet modules",
                   "OPTION_LIST"     : ["yes", "no"],
                   "VALIDATION_FUNC" : validate.validateOptions,
                   "DEFAULT_VALUE"   : "no",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_PUPPET_REMOVEMODULES",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                 ]

    groupDict = { "GROUP_NAME"            : "PUPPET",
                  "DESCRIPTION"           : "Puppet Config paramaters",
                  "PRE_CONDITION"         : utils.returnYes,
                  "PRE_CONDITION_MATCH"   : "yes",
                  "POST_CONDITION"        : False,
                  "POST_CONDITION_MATCH"  : True}

    controller.addGroup(groupDict, paramsList)


def initSequences(controller):
    puppetpresteps = [
             {'title': 'Clean Up', 'functions':[runCleanup]},
    ]
    controller.insertSequence("Clean Up", [], [], puppetpresteps, index=0)

    puppetsteps = [
             {'title': 'Getting Puppet modules', 'functions':[getPuppetModules]},
             {'title': 'Installing Puppet', 'functions':[installpuppet]},
             {'title': 'Copying Puppet modules/manifests', 'functions':[copyPuppetModules]},
             {'title': 'Applying Puppet manifests', 'functions':[applyPuppetManifest]},
    ]
    controller.addSequence("Puppet", [], [], puppetsteps)

    controller.CONF.setdefault('CONFIG_MANIFESTFILES', [])

def runCleanup():
    localserver = utils.ScriptRunner()
    localserver.append("rm -rf %s/*pp"%MANIFESTDIR)
    if controller.CONF["CONFIG_PUPPET_REMOVEMODULES"] == 'yes':
        localserver.append("rm -rf %s"%MODULEDIR)
    localserver.execute()

def getPuppetModules():
    localserver = utils.ScriptRunner()
    
    localserver.append('mkdir -p %s'%MODULEDIR)
    for repository, directory in PUPPET_MODULES:
        directory = os.path.join(MODULEDIR, directory)
        localserver.append('[ -d %s ] || git clone %s %s'%(directory, repository, directory))
    localserver.execute()

def installpuppet():
    for hostname in utils.gethostlist(controller.CONF):
        server = utils.ScriptRunner(hostname)
        server.append("rpm -q puppet || yum install -y puppet")
        server.execute()

def copyPuppetModules():
    server = utils.ScriptRunner()
    for hostname in utils.gethostlist(controller.CONF):
        server.append("tar -czf - puppet/manifests puppet/modules | ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@%s tar -C /etc -xzf -"%(hostname))
    server.execute()

def applyPuppetManifest():
    print
    for manifest in controller.CONF['CONFIG_MANIFESTFILES']:
        for hostname in utils.gethostlist(controller.CONF):
            if "/%s_"%hostname not in manifest: continue

            print "Applying "+ manifest
            server = utils.ScriptRunner(hostname)
            server.append("puppet apply /etc/puppet/manifests/%s"%os.path.split(manifest)[1])
            server.execute()

