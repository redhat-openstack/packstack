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
Plugin responsible for setting OpenStack global options
"""

import glob
import os
import uuid

from packstack.installer import basedefs
from packstack.installer import processors
from packstack.installer import utils
from packstack.installer import validators

from packstack.modules.common import filtered_hosts
from packstack.modules.common import is_all_in_one
from packstack.modules.documentation import update_params_usage
from packstack.modules.ospluginutils import appendManifestFile
from packstack.modules.ospluginutils import getManifestTemplate

# ------------- Prescript Packstack Plugin Initialization --------------

PLUGIN_NAME = "Prescript"
PLUGIN_NAME_COLORED = utils.color_text(PLUGIN_NAME, 'blue')


def initConfig(controller):
    default_ssh_key = os.path.join(os.environ["HOME"], ".ssh/*.pub")
    default_ssh_key = (glob.glob(default_ssh_key) + [""])[0]
    params = {
        "GLOBAL": [
            {"CMD_OPTION": "ssh-public-key",
             "PROMPT": (
                 "Enter the path to your ssh Public key to install on servers"
             ),
             "OPTION_LIST": [],
             "VALIDATORS": [
                 validators.validate_file,
                 validators.validate_sshkey
             ],
             "PROCESSORS": [processors.process_ssh_key],
             "DEFAULT_VALUE": default_ssh_key,
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_SSH_KEY",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "default-password",
             "PROMPT": (
                 "Enter a default password to be used. Leave blank for a "
                 "randomly generated one."
             ),
             "OPTION_LIST": [],
             "DEFAULT_VALUE": '',
             "MASK_INPUT": True,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_DEFAULT_PASSWORD",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": True,
             "CONDITION": False},

            {"CMD_OPTION": "mariadb-install",
             "PROMPT": "Should Packstack install MariaDB",
             "OPTION_LIST": ["y", "n"],
             "VALIDATORS": [validators.validate_options],
             "DEFAULT_VALUE": "y",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_MARIADB_INSTALL",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False,
             "DEPRECATES": ['CONFIG_MYSQL_INSTALL']},

            {"CMD_OPTION": "os-glance-install",
             "PROMPT": (
                 "Should Packstack install OpenStack Image Service (Glance)"
             ),
             "OPTION_LIST": ["y", "n"],
             "VALIDATORS": [validators.validate_options],
             "DEFAULT_VALUE": "y",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_GLANCE_INSTALL",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "os-cinder-install",
             "PROMPT": (
                 "Should Packstack install OpenStack Block Storage "
                 "(Cinder) service"
             ),
             "OPTION_LIST": ["y", "n"],
             "VALIDATORS": [validators.validate_options],
             "DEFAULT_VALUE": "y",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_CINDER_INSTALL",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "os-manila-install",
             "PROMPT": (
                 "Should Packstack install OpenStack Shared File System "
                 "(Manila) service"
             ),
             "OPTION_LIST": ["y", "n"],
             "VALIDATORS": [validators.validate_options],
             "DEFAULT_VALUE": "n",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_MANILA_INSTALL",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "os-nova-install",
             "PROMPT": (
                 "Should Packstack install OpenStack Compute (Nova) service"
             ),
             "OPTION_LIST": ["y", "n"],
             "VALIDATORS": [validators.validate_options],
             "DEFAULT_VALUE": "y",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_NOVA_INSTALL",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "os-neutron-install",
             "PROMPT": (
                 "Should Packstack install OpenStack Networking (Neutron) "
                 "service"
             ),
             "OPTION_LIST": ["y", "n"],
             "VALIDATORS": [validators.validate_options],
             "DEFAULT_VALUE": "y",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_NEUTRON_INSTALL",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "os-horizon-install",
             "PROMPT": (
                 "Should Packstack install OpenStack Dashboard (Horizon)"
             ),
             "OPTION_LIST": ["y", "n"],
             "VALIDATORS": [validators.validate_options],
             "DEFAULT_VALUE": "y",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_HORIZON_INSTALL",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "os-swift-install",
             "PROMPT": (
                 "Should Packstack install OpenStack Object Storage (Swift)"
             ),
             "OPTION_LIST": ["y", "n"],
             "VALIDATORS": [validators.validate_options],
             "DEFAULT_VALUE": "y",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_SWIFT_INSTALL",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "os-ceilometer-install",
             "PROMPT": (
                 "Should Packstack install OpenStack Metering (Ceilometer)"
             ),
             "OPTION_LIST": ["y", "n"],
             "VALIDATORS": [validators.validate_options],
             "DEFAULT_VALUE": "y",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_CEILOMETER_INSTALL",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "os-heat-install",
             "PROMPT": (
                 "Should Packstack install OpenStack Orchestration (Heat)"
             ),
             "OPTION_LIST": ["y", "n"],
             "VALIDATORS": [validators.validate_options],
             "DEFAULT_VALUE": "n",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_HEAT_INSTALL",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "os-sahara-install",
             "PROMPT": (
                 "Should Packstack install OpenStack Clustering (Sahara)"
             ),
             "OPTION_LIST": ["y", "n"],
             "VALIDATORS": [validators.validate_options],
             "DEFAULT_VALUE": "n",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_SAHARA_INSTALL",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "os-trove-install",
             "PROMPT": (
                 "Should Packstack install OpenStack Database (Trove)"
             ),
             "OPTION_LIST": ["y", "n"],
             "VALIDATORS": [validators.validate_options],
             "DEFAULT_VALUE": "n",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_TROVE_INSTALL",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "os-ironic-install",
             "PROMPT": (
                 "Should Packstack install OpenStack Bare Metal (Ironic)"
             ),
             "OPTION_LIST": ["y", "n"],
             "VALIDATORS": [validators.validate_options],
             "DEFAULT_VALUE": "n",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_IRONIC_INSTALL",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "os-client-install",
             "PROMPT": "Should Packstack install OpenStack client tools",
             "OPTION_LIST": ["y", "n"],
             "VALIDATORS": [validators.validate_options],
             "DEFAULT_VALUE": "y",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_CLIENT_INSTALL",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "ntp-servers",
             "PROMPT": ("Enter a comma separated list of NTP server(s). Leave "
                        "plain if Packstack should not install ntpd "
                        "on instances."),
             "OPTION_LIST": [],
             "DEFAULT_VALUE": '',
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_NTP_SERVERS",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "nagios-install",
             "PROMPT": (
                 "Should Packstack install Nagios to monitor OpenStack "
                 "hosts"
             ),
             "OPTION_LIST": ["y", "n"],
             "VALIDATORS": [validators.validate_options],
             "DEFAULT_VALUE": 'y',
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_NAGIOS_INSTALL",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "exclude-servers",
             "PROMPT": (
                 "Enter a comma separated list of server(s) to be excluded."
                 " Leave plain if you don't need to exclude any server."
             ),
             "OPTION_LIST": [],
             "DEFAULT_VALUE": '',
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "EXCLUDE_SERVERS",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "os-debug-mode",
             "PROMPT": "Do you want to run OpenStack services in debug mode",
             "OPTION_LIST": ["y", "n"],
             "DEFAULT_VALUE": "n",
             "VALIDATORS": [validators.validate_options],
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_DEBUG_MODE",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CONF_NAME": "CONFIG_CONTROLLER_HOST",
             "CMD_OPTION": "os-controller-host",
             "PROMPT": "Enter the IP address of the controller host",
             "OPTION_LIST": [],
             "VALIDATORS": [validators.validate_ip,
                            validators.validate_ssh],
             "DEFAULT_VALUE": utils.get_localhost_ip(),
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False,
             "DEPRECATES": ['CONFIG_CEILOMETER_HOST',
                            'CONFIG_CINDER_HOST',
                            'CONFIG_GLANCE_HOST',
                            'CONFIG_HORIZON_HOST',
                            'CONFIG_HEAT_HOST',
                            'CONFIG_IRONIC_HOST',
                            'CONFIG_KEYSTONE_HOST',
                            'CONFIG_NAGIOS_HOST',
                            'CONFIG_NEUTRON_SERVER_HOST',
                            'CONFIG_NEUTRON_LBAAS_HOSTS',
                            'CONFIG_NOVA_API_HOST',
                            'CONFIG_NOVA_CERT_HOST',
                            'CONFIG_NOVA_VNCPROXY_HOST',
                            'CONFIG_NOVA_SCHED_HOST',
                            'CONFIG_OSCLIENT_HOST',
                            'CONFIG_SWIFT_PROXY_HOSTS']},

            {"CONF_NAME": "CONFIG_COMPUTE_HOSTS",
             "CMD_OPTION": "os-compute-hosts",
             "PROMPT": (
                 "Enter list of IP addresses on which to install compute "
                 "service"
             ),
             "OPTION_LIST": [],
             "VALIDATORS": [validators.validate_multi_ip,
                            validators.validate_multi_ssh],
             "DEFAULT_VALUE": utils.get_localhost_ip(),
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False,
             "DEPRECATES": ['CONFIG_NOVA_COMPUTE_HOSTS']},

            {"CONF_NAME": "CONFIG_NETWORK_HOSTS",
             "CMD_OPTION": "os-network-hosts",
             "PROMPT": ("Enter list of IP addresses on which to install "
                        "network service"),
             "OPTION_LIST": [],
             "VALIDATORS": [validators.validate_multi_ip,
                            validators.validate_multi_ssh],
             "DEFAULT_VALUE": utils.get_localhost_ip(),
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False,
             "DEPRECATES": ['CONFIG_NEUTRON_L3_HOSTS',
                            'CONFIG_NEUTRON_DHCP_HOSTS',
                            'CONFIG_NEUTRON_METADATA_HOSTS',
                            'CONFIG_NOVA_NETWORK_HOSTS']},

            {"CMD_OPTION": "os-vmware",
             "PROMPT": (
                 "Do you want to use VMware vCenter as hypervisor and "
                 "datastore"
             ),
             "OPTION_LIST": ["y", "n"],
             "DEFAULT_VALUE": "n",
             "VALIDATORS": [validators.validate_options],
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_VMWARE_BACKEND",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "os-vmware",
             "PROMPT": (
                 "Do you want to use VMware vCenter as hypervisor and "
                 "datastore"
             ),
             "OPTION_LIST": ["y", "n"],
             "DEFAULT_VALUE": "n",
             "VALIDATORS": [validators.validate_options],
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_VMWARE_BACKEND",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "unsupported",
             "PROMPT": (
                 "Enable this on your own risk. Do you want to use "
                 "insupported parameters"
             ),
             "OPTION_LIST": ["y", "n"],
             "DEFAULT_VALUE": "n",
             "VALIDATORS": [validators.validate_options],
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_UNSUPPORTED",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},
        ],

        "VMWARE": [
            {"CMD_OPTION": "vcenter-host",
             "PROMPT": (
                 "Enter the IP address of the VMware vCenter server to use "
                 "with Nova"
             ),
             "OPTION_LIST": [],
             "VALIDATORS": [validators.validate_ip],
             "DEFAULT_VALUE": "",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME": "CONFIG_VCENTER_HOST",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "vcenter-username",
             "PROMPT": ("Enter the username to authenticate on VMware "
                        "vCenter server"),
             "DEFAULT_VALUE": "",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME": "CONFIG_VCENTER_USER",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "vcenter-password",
             "PROMPT": ("Enter the password to authenticate on VMware "
                        "vCenter server"),
             "DEFAULT_VALUE": "",
             "MASK_INPUT": True,
             "LOOSE_VALIDATION": True,
             "CONF_NAME": "CONFIG_VCENTER_PASSWORD",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "vcenter-cluster",
             "PROMPT": "Enter the name of the vCenter datastore",
             "DEFAULT_VALUE": "",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME": "CONFIG_VCENTER_CLUSTER_NAME",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},
        ],

        "UNSUPPORTED": [
            {"CONF_NAME": "CONFIG_STORAGE_HOST",
             "CMD_OPTION": "os-storage-host",
             "PROMPT": "Enter the IP address of the storage host",
             "OPTION_LIST": [],
             "VALIDATORS": [validators.validate_ip,
                            validators.validate_ssh],
             "DEFAULT_VALUE": utils.get_localhost_ip(),
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CONF_NAME": "CONFIG_SAHARA_HOST",
             "CMD_OPTION": "os-sahara-host",
             "PROMPT": "Enter the IP address of the Sahara host",
             "OPTION_LIST": [],
             "VALIDATORS": [validators.validate_ip,
                            validators.validate_ssh],
             "DEFAULT_VALUE": utils.get_localhost_ip(),
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},
        ]
    }
    update_params_usage(basedefs.PACKSTACK_DOC, params)

    def use_vcenter(config):
        return (config['CONFIG_NOVA_INSTALL'] == 'y' and
                config['CONFIG_VMWARE_BACKEND'] == 'y')

    def unsupported_enabled(config):
        return config['CONFIG_UNSUPPORTED'] == 'y'

    groups = [
        {"GROUP_NAME": "GLOBAL",
         "DESCRIPTION": "Global Options",
         "PRE_CONDITION": lambda x: 'yes',
         "PRE_CONDITION_MATCH": "yes",
         "POST_CONDITION": False,
         "POST_CONDITION_MATCH": True},

        {"GROUP_NAME": "VMWARE",
         "DESCRIPTION": "vCenter Config Parameters",
         "PRE_CONDITION": use_vcenter,
         "PRE_CONDITION_MATCH": True,
         "POST_CONDITION": False,
         "POST_CONDITION_MATCH": True},

        {"GROUP_NAME": "UNSUPPORTED",
         "DESCRIPTION": "Global unsupported options",
         "PRE_CONDITION": unsupported_enabled,
         "PRE_CONDITION_MATCH": True,
         "POST_CONDITION": False,
         "POST_CONDITION_MATCH": True}
    ]
    for group in groups:
        controller.addGroup(group, params[group['GROUP_NAME']])


def initSequences(controller):
    prescript_steps = [
        {'title': 'Setting up ssh keys',
         'functions': [install_keys]},
        {'title': 'Preinstalling Puppet and discovering hosts\' details',
         'functions': [preinstall_and_discover]},
        {'title': 'Adding pre install manifest entries',
         'functions': [create_manifest]},
    ]

    if controller.CONF['CONFIG_NTP_SERVERS']:
        prescript_steps.append(
            {'title': 'Installing time synchronization via NTP',
             'functions': [create_ntp_manifest]})
    else:
        controller.MESSAGES.append('Time synchronization installation was '
                                   'skipped. Please note that unsynchronized '
                                   'time on server instances might be problem '
                                   'for some OpenStack components.')
    controller.addSequence("Running pre install scripts", [], [],
                           prescript_steps)


# -------------------------- step functions --------------------------

def install_keys_on_host(hostname, sshkeydata):
    server = utils.ScriptRunner(hostname)
    # TODO replace all that with ssh-copy-id
    server.append("mkdir -p ~/.ssh")
    server.append("chmod 500 ~/.ssh")
    server.append("grep '%s' ~/.ssh/authorized_keys > /dev/null 2>&1 || "
                  "echo %s >> ~/.ssh/authorized_keys"
                  % (sshkeydata, sshkeydata))
    server.append("chmod 400 ~/.ssh/authorized_keys")
    server.append("restorecon -r ~/.ssh")
    server.execute()


def install_keys(config, messages):
    with open(config["CONFIG_SSH_KEY"]) as fp:
        sshkeydata = fp.read().strip()

    # If this is a --allinone install *and* we are running as root,
    # we can configure the authorized_keys file locally, avoid problems
    # if PasswordAuthentication is disabled.
    if is_all_in_one(config) and os.getuid() == 0:
        install_keys_on_host(None, sshkeydata)
    else:
        for hostname in filtered_hosts(config):
            if '/' in hostname:
                hostname = hostname.split('/')[0]
            install_keys_on_host(hostname, sshkeydata)


def preinstall_and_discover(config, messages):
    """Installs Puppet and it's dependencies and dependencies of Puppet
    modules' package and discovers information about all hosts.
    """
    config['HOST_LIST'] = list(filtered_hosts(config))

    local = utils.ScriptRunner()
    local.append('rpm -q --requires %s | egrep -v "^(rpmlib|\/|perl)"'
                 % basedefs.PUPPET_MODULES_PKG)
    # this can fail if there are no dependencies other than those
    # filtered out by the egrep expression.
    rc, modules_deps = local.execute(can_fail=False)

    # modules package might not be installed if we are running from source;
    # in this case we assume user knows what (s)he's doing and we don't
    # install modules dependencies
    errmsg = '%s is not installed' % basedefs.PUPPET_MODULES_PKG
    deps = list(basedefs.PUPPET_DEPENDENCIES)
    if errmsg not in modules_deps:
        deps.extend([i.strip() for i in modules_deps.split() if i.strip()])

    details = {}
    for hostname in config['HOST_LIST']:
        # install Puppet and it's dependencies
        server = utils.ScriptRunner(hostname)
        packages = ' '.join(deps)
        server.append('yum install -y %s' % packages)
        server.append('yum update -y %s' % packages)
        # yum does not fail if one of the packages is missing
        for package in deps:
            server.append('rpm -q --whatprovides %s' % package)
        server.execute()

        # create the packstack tmp directory
        server.clear()
        server.append('mkdir -p %s' % basedefs.PACKSTACK_VAR_DIR)
        # Separately create the tmp directory for this packstack run, this will
        # fail if the directory already exists
        host_dir = os.path.join(basedefs.PACKSTACK_VAR_DIR, uuid.uuid4().hex)
        server.append('mkdir --mode 0700 %s' % host_dir)
        for i in ('modules', 'resources'):
            server.append('mkdir --mode 0700 %s' % os.path.join(host_dir, i))
        server.execute()
        details.setdefault(hostname, {})['tmpdir'] = host_dir

        # discover other host info; Facter is installed as Puppet dependency,
        # so we let it do the work
        server.clear()
        server.append('facter -p')
        rc, stdout = server.execute()
        for line in stdout.split('\n'):
            try:
                key, value = line.split('=>', 1)
            except ValueError:
                # this line is probably some warning, so let's skip it
                continue
            else:
                details[hostname][key.strip()] = value.strip()

        # create a symbolic link to /etc/hiera.yaml to avoid warning messages
        # such as "Warning: Config file /etc/puppet/hiera.yaml not found,
        # using Hiera defaults"
        server.clear()
        server.append('[[ ! -L /etc/puppet/hiera.yaml ]] && '
                      'ln -s /etc/hiera.yaml /etc/puppet/hiera.yaml || '
                      'echo "hiera.yaml symlink already created"')
        server.append("sed -i 's;:datadir:.*;:datadir: "
                      "%s/hieradata;g' /etc/puppet/hiera.yaml"
                      % details[hostname]['tmpdir'])
        server.execute()
    config['HOST_DETAILS'] = details


def create_manifest(config, messages):
    key = 'CONFIG_DEBUG_MODE'
    config[key] = config[key] == 'y' and True or False

    for hostname in filtered_hosts(config):
        manifestfile = "%s_prescript.pp" % hostname
        manifestdata = getManifestTemplate("prescript")
        appendManifestFile(manifestfile, manifestdata)


def create_ntp_manifest(config, messages):
    srvlist = [i.strip()
               for i in config['CONFIG_NTP_SERVERS'].split(',')
               if i.strip()]
    config['CONFIG_NTP_SERVERS'] = ' '.join(srvlist)

    definiton = '\n'.join(['server %s' % i for i in srvlist])
    config['CONFIG_NTP_SERVER_DEF'] = '%s\n' % definiton

    marker = uuid.uuid4().hex[:16]

    for hostname in filtered_hosts(config):
        hostnfo = config['HOST_DETAILS'][hostname]
        releaseos = hostnfo['operatingsystem']
        releasever = hostnfo['operatingsystemmajrelease']

        # Configure chrony for Fedora or RHEL/CentOS 7
        if releaseos == 'Fedora' or releasever == '7':
            manifestdata = getManifestTemplate('chrony')
            appendManifestFile('%s_chrony.pp' % hostname,
                               manifestdata,
                               marker=marker)
        # For previous versions, configure ntpd
        else:
            manifestdata = getManifestTemplate('ntpd')
            appendManifestFile('%s_ntpd.pp' % hostname,
                               manifestdata,
                               marker=marker)
