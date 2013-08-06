"""
Installs and configures puppet
"""
import sys
import logging
import os
import platform
import time

from packstack.installer import utils
from packstack.installer import basedefs, output_messages
from packstack.installer.exceptions import ScriptRuntimeError

from packstack.modules.ospluginutils import (gethostlist,
                                             manifestfiles,
                                             scan_puppet_logfile,
                                             validate_puppet_logfile)

# Controller object will be initialized from main flow
controller = None

# Plugin name
PLUGIN_NAME = "OSPUPPET"
PLUGIN_NAME_COLORED = utils.color_text(PLUGIN_NAME, 'blue')

logging.debug("plugin %s loaded", __name__)

PUPPETDIR = os.path.abspath(os.path.join(basedefs.DIR_PROJECT_DIR, 'puppet'))
MODULEDIR = os.path.join(PUPPETDIR, "modules")


def initConfig(controllerObject):
    global controller
    controller = controllerObject
    logging.debug("Adding OpenStack Puppet configuration")
    paramsList = [
                 ]

    groupDict = {"GROUP_NAME"            : "PUPPET",
                 "DESCRIPTION"           : "Puppet Config parameters",
                 "PRE_CONDITION"         : lambda x: 'yes',
                 "PRE_CONDITION_MATCH"   : "yes",
                 "POST_CONDITION"        : False,
                 "POST_CONDITION_MATCH"  : True}

    controller.addGroup(groupDict, paramsList)


def getinstallhostlist(conf):
    list = []
    exclude_list = map(str.strip, conf['EXCLUDE_SERVERS'].split(','))
    for host in gethostlist(conf):
        if host not in exclude_list:
            list.append(host)
    return list


def initSequences(controller):
    puppetpresteps = [
             {'title': 'Clean Up', 'functions':[runCleanup]},
    ]
    controller.insertSequence("Clean Up", [], [], puppetpresteps, index=0)

    puppetsteps = [
             {'title': 'Installing Dependencies', 'functions':[installdeps]},
             {'title': 'Copying Puppet modules and manifests', 'functions':[copyPuppetModules]},
             {'title': 'Applying Puppet manifests', 'functions':[applyPuppetManifest]},
    ]
    controller.addSequence("Puppet", [], [], puppetsteps)


def runCleanup(config):
    localserver = utils.ScriptRunner()
    localserver.append("rm -rf %s/*pp" % basedefs.PUPPET_MANIFEST_DIR)
    localserver.execute()


def installdeps(config):
    for hostname in getinstallhostlist(controller.CONF):
        server = utils.ScriptRunner(hostname)
        for package in ("puppet", "openssh-clients", "tar", "nc"):
            server.append("rpm -q %s || yum install -y %s" % (package, package))
        server.execute()


def copyPuppetModules(config):
    os_modules = ' '.join(('apache', 'cinder', 'concat',
                           'create_resources', 'firewall',
                           'glance', 'horizon', 'inifile',
                           'keystone', 'memcached', 'mysql',
                           'nova', 'openstack', 'packstack',
                           'qpid', 'neutron', 'rsync', 'ssh', 'stdlib',
                           'swift', 'sysctl', 'tempest', 'vcsrepo',
                           'vlan', 'vswitch', 'xinetd'))

    # write puppet manifest to disk
    manifestfiles.writeManifests()

    server = utils.ScriptRunner()
    tar_opts = ""
    if platform.linux_distribution()[0] == "Fedora":
        tar_opts += "--exclude create_resources "
    for hostname in getinstallhostlist(controller.CONF):
        host_dir = controller.temp_map[hostname]
        puppet_dir = os.path.join(host_dir, basedefs.PUPPET_MANIFEST_RELATIVE)
        server.append("cd %s/puppet" % basedefs.DIR_PROJECT_DIR)
        # copy Packstack facts
        server.append("tar %s --dereference -cpzf - facts | "
                      "ssh -o StrictHostKeyChecking=no "
                          "-o UserKnownHostsFile=/dev/null "
                          "root@%s tar -C %s -xpzf -" % (tar_opts, hostname, host_dir))
        # copy Packstack manifests
        server.append("cd %s" % basedefs.PUPPET_MANIFEST_DIR)
        server.append("tar %s --dereference -cpzf - ../manifests | "
                      "ssh -o StrictHostKeyChecking=no "
                          "-o UserKnownHostsFile=/dev/null "
                          "root@%s tar -C %s -xpzf -" % (tar_opts, hostname, host_dir))

        # copy resources
        for path, localname in controller.resources.get(hostname, []):
            server.append("scp -o StrictHostKeyChecking=no "
                "-o UserKnownHostsFile=/dev/null %s root@%s:%s/resources/%s" %
                (path, hostname, host_dir, localname))

        # copy Puppet modules required by Packstack
        server.append("cd %s/puppet/modules" % basedefs.DIR_PROJECT_DIR)
        server.append("tar %s --dereference -cpzf - %s | "
                      "ssh -o StrictHostKeyChecking=no "
                          "-o UserKnownHostsFile=/dev/null "
                          "root@%s tar -C %s -xpzf -" %
                                (tar_opts, os_modules, hostname,
                                 os.path.join(host_dir, 'modules')))
    server.execute()


def waitforpuppet(currently_running):
    global controller
    log_len = 0
    twirl = ["-","\\","|","/"]
    while currently_running:
        for hostname, finished_logfile in currently_running:
            log_file = os.path.splitext(os.path.basename(finished_logfile))[0]
            space_len = basedefs.SPACE_LEN - len(log_file)
            if len(log_file) > log_len:
                log_len = len(log_file)
            if hasattr(sys.stdout, "isatty") and sys.stdout.isatty():
                twirl = twirl[-1:] + twirl[:-1]
                sys.stdout.write(("\rTesting if puppet apply is finished : %s" % log_file).ljust(40 + log_len))
                sys.stdout.write("[ %s ]" % twirl[0])
                sys.stdout.flush()
            try:
                # Once a remote puppet run has finished, we retrieve the log
                # file and check it for errors
                local_server = utils.ScriptRunner()
                log = os.path.join(basedefs.PUPPET_MANIFEST_DIR,
                                   os.path.basename(finished_logfile).replace(".finished", ".log"))
                local_server.append('scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@%s:%s %s' % (hostname, finished_logfile, log))
                # Errors are expected here if the puppet run isn't finished so we suppress logging them
                local_server.execute(logerrors=False)

                # If we got to this point the puppet apply has finished
                currently_running.remove((hostname, finished_logfile))

                # clean off the last "testing apply" msg
                if hasattr(sys.stdout, "isatty") and sys.stdout.isatty():
                    sys.stdout.write(("\r").ljust(45 + log_len))

            except ScriptRuntimeError, e:
                # the test raises an exception if the file doesn't exist yet
                # TO-DO: We need to start testing 'e' for unexpected exceptions
                time.sleep(3)
                continue

            # check log file for relevant notices
            controller.MESSAGES.extend(scan_puppet_logfile(log))

            # check the log file for errors
            validate_puppet_logfile(log)
            sys.stdout.write(("\r%s : " % log_file).ljust(basedefs.SPACE_LEN))
            print ("[ " + utils.color_text(output_messages.INFO_DONE, 'green') + " ]")


def applyPuppetManifest(config):
    print
    currently_running = []
    lastmarker = None
    for manifest, marker in manifestfiles.getFiles():
        # if the marker has changed then we don't want to proceed until
        # all of the previous puppet runs have finished
        if lastmarker != None and lastmarker != marker:
            waitforpuppet(currently_running)
        lastmarker = marker

        for hostname in getinstallhostlist(controller.CONF):
            if "%s_" % hostname not in manifest:
                continue

            host_dir = controller.temp_map[hostname]
            print "Applying " + manifest
            server = utils.ScriptRunner(hostname)

            man_path = os.path.join(controller.temp_map[hostname],
                                    basedefs.PUPPET_MANIFEST_RELATIVE,
                                    manifest)

            running_logfile = "%s.running" % man_path
            finished_logfile = "%s.finished" % man_path
            currently_running.append((hostname, finished_logfile))
            # The apache puppet module doesn't work if we set FACTERLIB
            # https://github.com/puppetlabs/puppetlabs-apache/pull/138
            if not (manifest.endswith('_horizon.pp') or manifest.endswith('_nagios.pp')):
                server.append("export FACTERLIB=$FACTERLIB:%s/facts" % host_dir)
            server.append("touch %s" % running_logfile)
            server.append("chmod 600 %s" % running_logfile)
            server.append("export PACKSTACK_VAR_DIR=%s" % host_dir)
            loglevel = ''
            if logging.root.level <= logging.DEBUG:
                loglevel = '--debug'
            command = "( flock %s/ps.lock puppet apply %s --modulepath %s/modules %s > %s 2>&1 < /dev/null ; mv %s %s ) > /dev/null 2>&1 < /dev/null &" % (host_dir, loglevel, host_dir, man_path, running_logfile, running_logfile, finished_logfile)
            server.append(command)
            server.execute()

    # wait for outstanding puppet runs befor exiting
    waitforpuppet(currently_running)
