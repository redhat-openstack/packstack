"""
Installs and configures puppet
"""
import logging
import os
import platform

from packstack.installer import basedefs
import packstack.installer.common_utils as utils

from packstack.modules.ospluginutils import gethostlist

# Controller object will be initialized from main flow
controller = None

# Plugin name
PLUGIN_NAME = "OSPUPPET"
PLUGIN_NAME_COLORED = utils.getColoredText(PLUGIN_NAME, basedefs.BLUE)

logging.debug("plugin %s loaded", __name__)

PUPPETDIR      = os.path.abspath(os.path.join(basedefs.DIR_PROJECT_DIR, 'puppet'))
MODULEDIR = os.path.join(PUPPETDIR, "modules")

def initConfig(controllerObject):
    global controller
    controller = controllerObject
    logging.debug("Adding Openstack Puppet configuration")
    paramsList = [
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
             {'title': 'Installing Puppet', 'functions':[installpuppet]},
             {'title': 'Copying Puppet modules/manifests', 'functions':[copyPuppetModules]},
             {'title': 'Applying Puppet manifests', 'functions':[applyPuppetManifest]},
    ]
    controller.addSequence("Puppet", [], [], puppetsteps)

    controller.CONF.setdefault('CONFIG_MANIFESTFILES', [])

def runCleanup():
    localserver = utils.ScriptRunner()
    localserver.append("rm -rf %s/*pp"%basedefs.PUPPET_MANIFEST_DIR)
    localserver.execute()

def installpuppet():
    for hostname in gethostlist(controller.CONF):
        server = utils.ScriptRunner(hostname)
        server.append("rpm -q puppet || yum install -y puppet")
        # disable epel if on rhel
        if controller.CONF["CONFIG_USE_EPEL"] == 'n':
            server.append("grep 'Red Hat Enterprise Linux' /etc/redhat-release && sed -i -e 's/enabled=1/enabled=0/g' /etc/yum.repos.d/epel.repo || echo -n ''")
        server.execute()

def copyPuppetModules():
    server = utils.ScriptRunner()
    tar_opts = ""
    if platform.linux_distribution()[0] == "Fedora":
        tar_opts += "--exclude create_resources "
    for hostname in gethostlist(controller.CONF):
        server.append("cd %s"%basedefs.DIR_PROJECT_DIR,)
        server.append("tar %s --dereference -czf - puppet/modules | ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@%s tar -C /etc -xzf -"%(tar_opts, hostname))
        server.append("cd %s"%basedefs.PUPPET_MANIFEST_DIR)
        server.append("tar %s --dereference -czf - ../manifests | ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@%s tar -C /etc/puppet -xzf -"%(tar_opts, hostname))
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

