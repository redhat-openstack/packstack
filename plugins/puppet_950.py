"""
Installs and configures puppet
"""
import logging
import os
import uuid

import engine_validators as validate
import basedefs
import common_utils as utils

from ospluginutils import gethostlist


# Controller object will be initialized from main flow
controller = None

# Plugin name
PLUGIN_NAME = "OSPUPPET"
PLUGIN_NAME_COLORED = utils.getColoredText(PLUGIN_NAME, basedefs.BLUE)

logging.debug("plugin %s loaded", __name__)

PUPPETDIR      = os.path.join(basedefs.DIR_PROJECT_DIR, 'puppet')
MODULEDIR = os.path.join(PUPPETDIR, "modules")
MANIFESTDIR = os.path.join(PUPPETDIR, "manifests")
PUPPET_MODULES = [
    ('https://github.com/puppetlabs/puppetlabs-glance.git', 'glance', "98770e6080288e958a4ef569c10855547ad71e16"),
    ('https://github.com/puppetlabs/puppetlabs-horizon.git', 'horizon', "1596b6515bd79a6d89c565924a9420717e78185f"),
    ('https://github.com/puppetlabs/puppetlabs-keystone.git', 'keystone', "823a40ea5d53aa8da2c7cc13529987660e4ec5b9"),
    ('https://github.com/puppetlabs/puppetlabs-nova.git', 'nova', "6e899cd211ec8544ef6c68a98ce2310b337383c3"),
    ('https://github.com/puppetlabs/puppetlabs-openstack.git', 'openstack', "9c72fa0d25828a918beb0593bab6ae6c0b42da09"),
    ('https://github.com/puppetlabs/puppetlabs-swift.git', 'swift', "05d44d8e784f6d649086504e2d53ff1dde17bd3f"),
    ('https://github.com/puppetlabs/puppetlabs-stdlib.git', 'stdlib', "6961179007dce76d7fb9bd1fc361273acb4129a7"),
    ('https://github.com/puppetlabs/puppetlabs-sysctl.git', 'sysctl', "c4486acc2d66de857dbccd8b4b945ea803226705"),
    ('https://github.com/puppetlabs/puppetlabs-mysql.git', 'mysql', "832783040ac30413fd7c0b583b94faaedb7aea95"),
    ('https://github.com/puppetlabs/puppetlabs-concat.git', 'concat', "031bf261289dcbb32e63b053ed5b3a82117698c0"),
    ('https://github.com/puppetlabs/puppetlabs-create_resources.git', 'create_resources', "28584b0ed187fda119b3c44d468cafe7d3e1e980"),
    ('https://github.com/puppetlabs/puppetlabs-rsync.git', 'rsync', "357d51f3a6a22bc3da842736176c3510e507b4fb"),
    ('https://github.com/puppetlabs/puppetlabs-xinetd.git', 'xinetd', "e06e82ecc035d1cb12140ad381ae03c70ac17f66"),
    ('https://github.com/lstanden/puppetlabs-firewall.git', 'firewall', "6106fb5404480ac7c883bddd503e0fc9f2698750"),
    ('https://github.com/saz/puppet-memcached.git', 'memcached', "811822306b3db89d16d68a566683beb622c3a83f"),
    ('https://github.com/saz/puppet-ssh.git', 'ssh', "c77376c20830bdd0049b4c6c410fb9e5880e6ef5"),
    ('https://github.com/derekhiggins/puppet-qpid.git', 'qpid', "4ada31cbfc99b28dfb5eed449ff609d19a5b90ec"),
    ('https://github.com/derekhiggins/puppet-vlan.git', 'vlan', "e4ec0e0fa3ac2b93e65ae7501ce431a02f0da132")
]

def initConfig(controllerObject):
    global controller
    controller = controllerObject
    logging.debug("Adding Openstack Puppet configuration")
    paramsList = [
                  {"CMD_OPTION"      : "remove-puppetmodules",
                   "USAGE"           : "Causes the Puppet modules to be removed (if present), and as a result re-cloned from git",
                   "PROMPT"          : "Should we remove the Puppet modules",
                   "OPTION_LIST"     : ["y", "n"],
                   "VALIDATION_FUNC" : validate.validateOptions,
                   "DEFAULT_VALUE"   : "n",
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
    if controller.CONF["CONFIG_PUPPET_REMOVEMODULES"] == 'y':
        localserver.append("rm -rf %s"%MODULEDIR)
    localserver.execute()

def getPuppetModules():
    localserver = utils.ScriptRunner()
    
    localserver.append('mkdir -p %s'%MODULEDIR)
    for repository, directory, branch in PUPPET_MODULES:
        directory = os.path.join(MODULEDIR, directory)
        localserver.append('[ -d %s ] || git clone %s %s'%(directory, repository, directory))
        if branch:
            localserver.append('cd %s ;  git checkout %s ; cd -'%(directory, branch))
    localserver.execute()

def installpuppet():
    for hostname in gethostlist(controller.CONF):
        server = utils.ScriptRunner(hostname)
        server.append("rpm -q puppet || yum install -y puppet")
        # disable epel if on rhel
        server.append("grep 'Red Hat Enterprise Linux' /etc/redhat-release && sed -i -e 's/enabled=1/enabled=0/g' /etc/yum.repos.d/epel.repo || echo -n ''")
        server.execute()

def copyPuppetModules():
    server = utils.ScriptRunner()
    for hostname in gethostlist(controller.CONF):
        server.append("cd %s"%basedefs.DIR_PROJECT_DIR,)
        server.append("tar -czf - puppet/manifests puppet/modules | ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@%s tar -C /etc -xzf -"%(hostname))
    server.execute()

def applyPuppetManifest():
    print
    for manifest in controller.CONF['CONFIG_MANIFESTFILES']:
        for hostname in gethostlist(controller.CONF):
            if "/%s_"%hostname not in manifest: continue

            print "Applying "+ manifest
            server = utils.ScriptRunner(hostname)
            server.append("puppet apply /etc/puppet/manifests/%s"%os.path.split(manifest)[1])
            server.execute()

