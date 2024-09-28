# -*- coding: utf-8 -*-
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Installs and configures Puppet
"""

import logging
import os
import sys
import time

from packstack.installer import utils
from packstack.installer import basedefs
from packstack.installer.exceptions import PuppetError
from packstack.installer.exceptions import ScriptRuntimeError
from packstack.installer.utils import split_hosts

from packstack.modules.common import filtered_hosts
from packstack.modules.ospluginutils import appendManifestFile
from packstack.modules.ospluginutils import generateHieraDataFile
from packstack.modules.ospluginutils import getManifestTemplate
from packstack.modules.ospluginutils import manifestfiles
from packstack.modules.puppet import validate_logfile
from packstack.modules.puppet import scan_logfile


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
        {'title': 'Preparing Puppet manifests',
            'functions': [prepare_puppet_modules]},
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
                                    'root@[%s]:%s %s'
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


def copy_puppet_modules(config, messages):
    os_modules = ' '.join(('aodh', 'apache', 'ceilometer', 'cinder', 'concat',
                           'firewall', 'glance', 'gnocchi', 'heat', 'horizon',
                           'inifile', 'ironic', 'keystone', 'magnum', 'manila',
                           'memcached', 'mysql', 'neutron', 'nova', 'nssdb',
                           'openstacklib', 'oslo', 'ovn', 'packstack',
                           'placement', 'rabbitmq', 'redis', 'remote', 'rsync',
                           'ssh', 'stdlib', 'swift', 'sysctl', 'systemd',
                           'tempest', 'trove', 'vcsrepo', 'vswitch', 'xinetd'))

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
                          "%s root@[%s]:%s/resources/%s" %
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
            print("Applying %s" % manifest)
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
            server.append("export LANG=C.UTF-8")
            cmd = ("( flock %s/ps.lock "
                   "puppet apply %s --modulepath %s/modules %s > %s "
                   "2>&1 < /dev/null ; "
                   "mv %s %s ) > /dev/null 2>&1 < /dev/null &"
                   % (host_dir, loglevel, host_dir, man_path, running_logfile,
                      running_logfile, finished_logfile))
            server.append(cmd)
            server.execute(log=logcmd)

    # wait for outstanding puppet runs before exiting
    wait_for_puppet(currently_running, messages)


def prepare_puppet_modules(config, messages):
    network_hosts = split_hosts(config['CONFIG_NETWORK_HOSTS'])
    compute_hosts = split_hosts(config['CONFIG_COMPUTE_HOSTS'])

    manifestdata = getManifestTemplate("controller")
    manifestfile = "%s_controller.pp" % config['CONFIG_CONTROLLER_HOST']
    appendManifestFile(manifestfile, manifestdata, marker='controller')

    for host in network_hosts:
        manifestdata = getManifestTemplate("network")
        manifestfile = "%s_network.pp" % host
        appendManifestFile(manifestfile, manifestdata, marker='network')

    for host in compute_hosts:
        manifestdata = getManifestTemplate("compute")
        manifestfile = "%s_compute.pp" % host
        appendManifestFile(manifestfile, manifestdata, marker='compute')

    manifestdata = getManifestTemplate("controller_post")
    manifestfile = "%s_controller_post.pp" % config['CONFIG_CONTROLLER_HOST']
    appendManifestFile(manifestfile, manifestdata, marker='controller')


def finalize(config, messages):
    for hostname in filtered_hosts(config):
        server = utils.ScriptRunner(hostname)
        server.append("installed=$(rpm -q kernel --last | head -n1 | "
                      "sed 's/kernel-\([a-z0-9\.\_\-]*\).*/\\1/g')")    # noqa: W605
        server.append("loaded=$(uname -r | head -n1)")
        server.append('[ "$loaded" == "$installed" ]')
        try:
            rc, out = server.execute()
        except ScriptRuntimeError:
            messages.append('Because of the kernel update the host %s '
                            'requires reboot.' % hostname)
