"""
Installs and configures puppet
"""
import logging
import os
import platform
import time

import packstack.installer.common_utils as utils
from packstack.installer import basedefs
from packstack.installer.exceptions import ScriptRuntimeError

from packstack.modules.ospluginutils import gethostlist,\
                                            manifestfiles,\
                                            validate_puppet_logfile

# Controller object will be initialized from main flow
controller = None

# Plugin name
PLUGIN_NAME = "OSPUPPET"
PLUGIN_NAME_COLORED = utils.getColoredText(PLUGIN_NAME, basedefs.BLUE)

logging.debug("plugin %s loaded", __name__)

PUPPETDIR = os.path.abspath(os.path.join(basedefs.DIR_PROJECT_DIR, 'puppet'))
MODULEDIR = os.path.join(PUPPETDIR, "modules")


def initConfig(controllerObject):
    global controller
    controller = controllerObject
    logging.debug("Adding Openstack Puppet configuration")
    paramsList = [
                 ]

    groupDict = {"GROUP_NAME"            : "PUPPET",
                 "DESCRIPTION"           : "Puppet Config parameters",
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


def runCleanup():
    localserver = utils.ScriptRunner()
    localserver.append("rm -rf %s/*pp" % basedefs.PUPPET_MANIFEST_DIR)
    localserver.execute()


def installpuppet():
    for hostname in gethostlist(controller.CONF):
        server = utils.ScriptRunner(hostname)
        server.append("rpm -q puppet || yum install -y puppet")
        server.execute()


def copyPuppetModules():
    server = utils.ScriptRunner()
    tar_opts = ""
    if platform.linux_distribution()[0] == "Fedora":
        tar_opts += "--exclude create_resources "
    for hostname in gethostlist(controller.CONF):
        server.append("cd %s/puppet" % basedefs.DIR_PROJECT_DIR)
        server.append("tar %s --dereference -czf - modules facts | ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@%s tar -C %s -xzf -" % (tar_opts, hostname, basedefs.VAR_DIR))
        server.append("cd %s" % basedefs.PUPPET_MANIFEST_DIR)
        server.append("tar %s --dereference -czf - ../manifests | ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@%s tar -C %s -xzf -" % (tar_opts, hostname, basedefs.VAR_DIR))
    server.execute()


def waitforpuppet(currently_running):
    while currently_running:
        for hostname, finished_logfile in currently_running:
            print "Testing if puppet apply is finished : %s" % os.path.splitext(os.path.basename(finished_logfile))[0],
            try:
                # Once a remote puppet run has finished, we retrieve the log
                # file and check it for errors
                local_server = utils.ScriptRunner()
                log = finished_logfile.replace(".finished", ".log")
                local_server.append('scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@%s:%s %s' % (hostname, finished_logfile, log))
                # Errors are expected here if the puppet run isn't finished so we suppress logging them
                local_server.execute(logerrors=False)

                # If we got to this point the puppet apply has finished
                currently_running.remove((hostname, finished_logfile))

            except ScriptRuntimeError, e:
                # the test raises an exception if the file doesn't exist yet
                # TO-DO: We need to start testing 'e' for unexpected exceptions
                time.sleep(3)
                print
                continue

            # check the log file for errors
            validate_puppet_logfile(log)
            print "OK"


def applyPuppetManifest():
    print
    currently_running = []
    lastmarker = None
    for manifest, marker in manifestfiles.getFiles():
        # if the marker has changed then we don't want to proceed until
        # all of the previous puppet runs have finished
        if lastmarker != None and lastmarker != marker:
            waitforpuppet(currently_running)
        lastmarker = marker

        for hostname in gethostlist(controller.CONF):
            if "/%s_" % hostname not in manifest:
                continue

            print "Applying " + manifest
            server = utils.ScriptRunner(hostname)

            running_logfile = "%s.running" % manifest
            finished_logfile = "%s.finished" % manifest
            currently_running.append((hostname, finished_logfile))
            command = "( flock %s/ps.lock puppet apply --modulepath %s/modules %s > %s 2>&1 < /dev/null ; mv %s %s ) > /dev/null 2>&1 < /dev/null &" % (basedefs.VAR_DIR, basedefs.VAR_DIR, manifest, running_logfile, running_logfile, finished_logfile)
            server.append("export FACTERLIB=%s/facts"%basedefs.VAR_DIR)
            server.append(command)
            server.execute()

    # wait for outstanding puppet runs befor exiting
    waitforpuppet(currently_running)
