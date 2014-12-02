# -*- coding: utf-8 -*-

"""
Installs and configures Puppet
"""

import sys
import logging
import os
import time

from packstack.installer import utils
from packstack.installer import basedefs
from packstack.installer.exceptions import ScriptRuntimeError, PuppetError

from packstack.modules.common import filtered_hosts
from packstack.modules.ospluginutils import (manifestfiles,
                                             generateHieraDataFile)
from packstack.modules.puppet import scan_logfile, validate_logfile


# ------------- Puppet Packstack Plugin Initialization --------------

PLUGIN_NAME = "Puppet"
PLUGIN_NAME_COLORED = utils.color_text(PLUGIN_NAME, 'blue')


PUPPET_DIR = os.environ.get('PACKSTACK_PUPPETDIR',
                            '/usr/share/openstack-puppet/')
MODULE_DIR = os.path.join(PUPPET_DIR, 'modules')


def initConfig(controller):
    group = {"GROUP_NAME": "PUPPET",
             "DESCRIPTION": "Puppet Config parameters",
             "PRE_CONDITION": lambda x: 'yes',
             "PRE_CONDITION_MATCH": "yes",
             "POST_CONDITION": False,
             "POST_CONDITION_MATCH": True}
    controller.addGroup(group, [])


def initSequences(controller):
    puppetpresteps = [
        {'title': 'Clean Up', 'functions': [run_cleanup]},
    ]
    controller.insertSequence("Clean Up", [], [], puppetpresteps, index=0)

    puppetsteps = [
        {'title': 'Installing Dependencies',
            'functions': [install_deps]},
        {'title': 'Copying Puppet modules and manifests',
            'functions': [copy_puppet_modules]},
        {'title': 'Applying Puppet manifests',
            'functions': [apply_puppet_manifest]},
        {'title': 'Finalizing',
            'functions': [finalize]}
    ]
    controller.addSequence("Puppet", [], [], puppetsteps)


# ------------------------- helper functions -------------------------

def wait_for_puppet(currently_running, messages):
    log_len = 0
    twirl = ["-", "\\", "|", "/"]
    while currently_running:
        for hostname, finished_logfile in currently_running:
            log_file = os.path.splitext(os.path.basename(finished_logfile))[0]
            space_len = basedefs.SPACE_LEN - len(log_file)
            if len(log_file) > log_len:
                log_len = len(log_file)
            if hasattr(sys.stdout, "isatty") and sys.stdout.isatty():
                twirl = twirl[-1:] + twirl[:-1]
                sys.stdout.write(("\rTesting if puppet apply is finished: %s"
                                 % log_file).ljust(40 + log_len))
                sys.stdout.write("[ %s ]" % twirl[0])
                sys.stdout.flush()
            try:
                # Once a remote puppet run has finished, we retrieve the log
                # file and check it for errors
                local_server = utils.ScriptRunner()
                log = os.path.join(basedefs.PUPPET_MANIFEST_DIR,
                                   os.path.basename(finished_logfile))
                log = log.replace(".finished", ".log")
                local_server.append('scp -o StrictHostKeyChecking=no '
                                    '-o UserKnownHostsFile=/dev/null '
                                    'root@%s:%s %s'
                                    % (hostname, finished_logfile, log))
                # To not pollute logs we turn of logging of command execution
                local_server.execute(log=False)

                # If we got to this point the puppet apply has finished
                currently_running.remove((hostname, finished_logfile))

                # clean off the last "testing apply" msg
                if hasattr(sys.stdout, "isatty") and sys.stdout.isatty():
                    sys.stdout.write(("\r").ljust(45 + log_len))

            except ScriptRuntimeError:
                # the test raises an exception if the file doesn't exist yet
                # TO-DO: We need to start testing 'e' for unexpected exceptions
                time.sleep(3)
                continue

            # check log file for relevant notices
            messages.extend(scan_logfile(log))

            # check the log file for errors
            sys.stdout.write('\r')
            try:
                validate_logfile(log)
                state = utils.state_message('%s:' % log_file, 'DONE', 'green')
                sys.stdout.write('%s\n' % state)
                sys.stdout.flush()
            except PuppetError:
                state = utils.state_message('%s:' % log_file, 'ERROR', 'red')
                sys.stdout.write('%s\n' % state)
                sys.stdout.flush()
                raise


# -------------------------- step functions --------------------------

def run_cleanup(config, messages):
    localserver = utils.ScriptRunner()
    localserver.append("rm -rf %s/*pp" % basedefs.PUPPET_MANIFEST_DIR)
    localserver.execute()


def install_deps(config, messages):
    deps = ["puppet", "hiera", "openssh-clients", "tar", "nc"]
    modules_pkg = 'openstack-puppet-modules'

    local = utils.ScriptRunner()
    local.append('rpm -q --requires %s | egrep -v "^(rpmlib|\/|perl)"'
                 % modules_pkg)

    # This can fail if there are no dependencies other than those
    # filtered out by the egrep expression.
    rc, modules_deps = local.execute(can_fail=False)

    # Modules package might not be installed if we are running from source.
    # In this case we assume user knows what (s)he's doing and we don't
    # install modules dependencies
    if ('%s is not installed' % modules_pkg) not in modules_deps:
        modules_deps = [i.strip() for i in modules_deps.split() if i.strip()]
        deps.extend(modules_deps)

    for hostname in filtered_hosts(config):
        server = utils.ScriptRunner(hostname)
        packages = ' '.join(deps)
        server.append("yum install -y %s" % packages)
        server.append("yum update -y %s" % packages)
        # yum does not fail if one of the packages is missing
        for package in deps:
            server.append("rpm -q --whatprovides %s" % (package))

        # To avoid warning messages such as
        # "Warning: Config file /etc/puppet/hiera.yaml not found, using Hiera
        # defaults". We create a symbolic link to /etc/hiera.yaml.
        server.append('[[ ! -L /etc/puppet/hiera.yaml ]] && '
                      'ln -s /etc/hiera.yaml /etc/puppet/hiera.yaml || '
                      'echo "hiera.yaml symlink already created"')

        server.append("sed -i 's;:datadir:.*;:datadir: "
                      "%s/hieradata;g' /etc/puppet/hiera.yaml"
                      % config['HOST_DETAILS'][hostname]['tmpdir'])

        server.execute()


def copy_puppet_modules(config, messages):
    os_modules = ' '.join(('apache', 'ceilometer', 'certmonger', 'cinder',
                           'concat', 'firewall', 'glance', 'heat', 'horizon',
                           'inifile', 'keystone', 'memcached', 'mongodb',
                           'mysql', 'neutron', 'nova', 'nssdb', 'openstack',
                           'packstack', 'qpid', 'rabbitmq', 'redis', 'remote',
                           'rsync', 'sahara', 'ssh', 'stdlib', 'swift',
                           'sysctl', 'tempest', 'vcsrepo', 'vlan', 'vswitch',
                           'xinetd', 'openstacklib'))

    # write puppet manifest to disk
    manifestfiles.writeManifests()
    # write hieradata file to disk
    generateHieraDataFile()

    server = utils.ScriptRunner()
    for hostname in filtered_hosts(config):
        host_dir = config['HOST_DETAILS'][hostname]['tmpdir']
        # copy hiera defaults.yaml file
        server.append("cd %s" % basedefs.HIERADATA_DIR)
        server.append("tar --dereference -cpzf - ../hieradata | "
                      "ssh -o StrictHostKeyChecking=no "
                      "-o UserKnownHostsFile=/dev/null "
                      "root@%s tar -C %s -xpzf -" % (hostname, host_dir))

        # copy Packstack manifests
        server.append("cd %s/puppet" % basedefs.DIR_PROJECT_DIR)
        server.append("cd %s" % basedefs.PUPPET_MANIFEST_DIR)
        server.append("tar --dereference -cpzf - ../manifests | "
                      "ssh -o StrictHostKeyChecking=no "
                      "-o UserKnownHostsFile=/dev/null "
                      "root@%s tar -C %s -xpzf -" % (hostname, host_dir))

        # copy resources
        resources = config.get('RESOURCES', {})
        for path, localname in resources.get(hostname, []):
            server.append("scp -o StrictHostKeyChecking=no "
                          "-o UserKnownHostsFile=/dev/null "
                          "%s root@%s:%s/resources/%s" %
                          (path, hostname, host_dir, localname))

        # copy Puppet modules required by Packstack
        server.append("cd %s" % MODULE_DIR)
        server.append("tar --dereference -cpzf - %s | "
                      "ssh -o StrictHostKeyChecking=no "
                      "-o UserKnownHostsFile=/dev/null "
                      "root@%s tar -C %s -xpzf -" %
                      (os_modules, hostname,
                       os.path.join(host_dir, 'modules')))
    server.execute()


def apply_puppet_manifest(config, messages):
    if config.get("DRY_RUN"):
        return
    currently_running = []
    lastmarker = None
    loglevel = ''
    logcmd = False
    if logging.root.level <= logging.DEBUG:
        loglevel = '--debug'
        logcmd = True
    for manifest, marker in manifestfiles.getFiles():
        # if the marker has changed then we don't want to proceed until
        # all of the previous puppet runs have finished
        if lastmarker is not None and lastmarker != marker:
            wait_for_puppet(currently_running, messages)
        lastmarker = marker

        for hostname in filtered_hosts(config):
            if "%s_" % hostname not in manifest:
                continue

            host_dir = config['HOST_DETAILS'][hostname]['tmpdir']
            print "Applying %s" % manifest
            server = utils.ScriptRunner(hostname)

            man_path = os.path.join(config['HOST_DETAILS'][hostname]['tmpdir'],
                                    basedefs.PUPPET_MANIFEST_RELATIVE,
                                    manifest)

            running_logfile = "%s.running" % man_path
            finished_logfile = "%s.finished" % man_path
            currently_running.append((hostname, finished_logfile))

            server.append("touch %s" % running_logfile)
            server.append("chmod 600 %s" % running_logfile)
            server.append("export PACKSTACK_VAR_DIR=%s" % host_dir)
            cmd = ("( flock %s/ps.lock "
                   "puppet apply %s --modulepath %s/modules %s > %s "
                   "2>&1 < /dev/null ; "
                   "mv %s %s ) > /dev/null 2>&1 < /dev/null &"
                   % (host_dir, loglevel, host_dir, man_path, running_logfile,
                      running_logfile, finished_logfile))
            server.append(cmd)
            server.execute(log=logcmd)

    # wait for outstanding puppet runs befor exiting
    wait_for_puppet(currently_running, messages)


def finalize(config, messages):
    for hostname in filtered_hosts(config):
        server = utils.ScriptRunner(hostname)
        server.append("installed=$(rpm -q kernel --last | head -n1 | "
                      "sed 's/kernel-\([a-z0-9\.\_\-]*\).*/\\1/g')")
        server.append("loaded=$(uname -r | head -n1)")
        server.append('[ "$loaded" == "$installed" ]')
        try:
            rc, out = server.execute()
        except ScriptRuntimeError:
            messages.append('Because of the kernel update the host %s '
                            'requires reboot.' % hostname)
