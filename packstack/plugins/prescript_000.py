# -*- coding: utf-8 -*-

"""
Plugin responsible for setting OpenStack global options
"""

import glob
import logging
import os
import re
import uuid

from packstack.installer import (basedefs, exceptions, processors, utils,
                                 validators)

from packstack.modules.common import filtered_hosts, is_all_in_one
from packstack.modules.ospluginutils import (getManifestTemplate,
                                             appendManifestFile)


#------------------ oVirt installer initialization ------------------

PLUGIN_NAME = "Prescript"
PLUGIN_NAME_COLORED = utils.color_text(PLUGIN_NAME, 'blue')


def initConfig(controller):
    default_ssh_key = os.path.expanduser('~/.ssh/*.pub')
    default_ssh_key = (glob.glob(default_ssh_key) + [""])[0]
    params = {
        "GLOBAL": [
            {"CMD_OPTION": "ssh-public-key",
             "USAGE": (
                "Path to a Public key to install on servers. If a usable "
                "key has not been installed on the remote servers the user "
                "will be prompted for a password and this key will be "
                "installed so the password will not be required again"
             ),
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

            {"CMD_OPTION": "mariadb-install",
             "USAGE": (
                "Set to 'y' if you would like Packstack to install MariaDB"
             ),
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
             "USAGE": (
                "Set to 'y' if you would like Packstack to install "
                "OpenStack Image Service (Glance)"
             ),
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
             "USAGE": (
                "Set to 'y' if you would like Packstack to install "
                "OpenStack Block Storage (Cinder)"
             ),
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

            {"CMD_OPTION": "os-nova-install",
             "USAGE": (
                "Set to 'y' if you would like Packstack to install "
                "OpenStack Compute (Nova)"
             ),
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
             "USAGE": (
                "Set to 'y' if you would like Packstack to install "
                "OpenStack Networking (Neutron). Otherwise Nova Network "
                "will be used."
             ),
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
             "USAGE": (
                "Set to 'y' if you would like Packstack to install "
                "OpenStack Dashboard (Horizon)"
             ),
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
             "USAGE": (
                "Set to 'y' if you would like Packstack to install "
                "OpenStack Object Storage (Swift)"
             ),
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
             "USAGE": (
                "Set to 'y' if you would like Packstack to install "
                "OpenStack Metering (Ceilometer)"
             ),
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
             "USAGE": (
                "Set to 'y' if you would like Packstack to install "
                "OpenStack Orchestration (Heat)"
             ),
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

            {"CMD_OPTION": "os-client-install",
             "USAGE": (
                "Set to 'y' if you would like Packstack to install "
                "the OpenStack Client packages. An admin \"rc\" file will "
                "also be installed"
             ),
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
             "USAGE": ("Comma separated list of NTP servers. Leave plain if "
                       "Packstack should not install ntpd on instances."),
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
             "USAGE": (
                "Set to 'y' if you would like Packstack to install Nagios "
                "to monitor OpenStack hosts"
             ),
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
             "USAGE": (
                "Comma separated list of servers to be excluded from "
                "installation in case you are running Packstack the second "
                "time with the same answer file and don't want Packstack "
                "to touch these servers. Leave plain if you don't need to "
                "exclude any server."
             ),
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
             "USAGE": (
                "Set to 'y' if you want to run OpenStack services in debug "
                "mode. Otherwise set to 'n'."
             ),
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
             "USAGE": (
                "The IP address of the server on which to install OpenStack"
                " services specific to controller role such as API servers,"
                " Horizon, etc."
             ),
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
             "USAGE": (
                "The list of IP addresses of the server on which to install"
                " the Nova compute service"
             ),
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
             "USAGE": ("The list of IP addresses of the server on which "
                       "to install the network service such as Nova "
                       "network or Neutron"),
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
             "USAGE": (
                "Set to 'y' if you want to use VMware vCenter as hypervisor"
                " and storage. Otherwise set to 'n'."
             ),
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
             "USAGE": (
                "Set to 'y' if you want to use VMware vCenter as hypervisor"
                " and storage. Otherwise set to 'n'."
             ),
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
             "USAGE": (
                "Set to 'y' if you want to use unsupported parameters. "
                "This should be used only if you know what you are doing."
                "Issues caused by using unsupported options won't be fixed "
                "before next major release."
             ),
             "PROMPT": (
                "Enable this on your own risk. Do you want to use unsupported "
                "parameters"
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
             "USAGE": "The IP address of the VMware vCenter server",
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
             "USAGE": "The username to authenticate to VMware vCenter server",
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
             "USAGE": "The password to authenticate to VMware vCenter server",
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
             "USAGE": "The name of the vCenter cluster",
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
             "USAGE": (
                "(Unsupported!) The IP address of the server on which "
                "to install OpenStack services specific to storage servers "
                "such as Glance and Cinder."
             ),
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
        ]
    }

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
        {'title': 'Discovering hosts\' details',
         'functions': [discover]},
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


#-------------------------- step functions --------------------------

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


def discover(config, messages):
    """
    Discovers details about hosts.
    """
    # TODO: Once Controller is refactored, move this function to it (facter can
    #       be used for that too).
    details = {}
    release_regexp = re.compile(r'^(?P<OS>.*) release (?P<release>[\d\.]*)')
    config['HOST_LIST'] = list(filtered_hosts(config))
    for host in config['HOST_LIST']:
        details.setdefault(host, {})
        server = utils.ScriptRunner(host)
        # discover OS and release
        server.append('cat /etc/redhat-release')
        try:
            rc, out = server.execute()
            match = release_regexp.search(out)
            if not match:
                raise exceptions.ScriptRuntimeError()
        except exceptions.ScriptRuntimeError:
            details[host]['os'] = 'Unknown'
            details[host]['release'] = 'Unknown'
        else:
            opsys = match.group('OS')
            for pattern, surr in [('^Red Hat Enterprise Linux.*', 'RHEL'),
                                  ('^Fedora.*', 'Fedora'),
                                  ('^CentOS.*', 'CentOS'),
                                  ('^Scientific Linux.*', 'SL')]:
                opsys = re.sub(pattern, surr, opsys)
            details[host]['os'] = opsys
            details[host]['release'] = match.group('release')

        # Create the packstack tmp directory
        server.clear()
        server.append("mkdir -p %s" % basedefs.PACKSTACK_VAR_DIR)
        # Separately create the tmp directory for this packstack run, this will
        # fail if the directory already exists
        host_dir = os.path.join(basedefs.PACKSTACK_VAR_DIR, uuid.uuid4().hex)
        server.append("mkdir --mode 0700 %s" % host_dir)
        for i in ('modules', 'resources'):
            server.append("mkdir --mode 0700 %s" % os.path.join(host_dir, i))
        server.execute()
        details[host]['tmpdir'] = host_dir
    config['HOST_DETAILS'] = details


def create_manifest(config, messages):
    key = 'CONFIG_DEBUG_MODE'
    config[key] = config[key] == 'y' and 'true' or 'false'

    for hostname in filtered_hosts(config):
        manifestfile = "%s_prescript.pp" % hostname
        manifestdata = getManifestTemplate("prescript.pp")
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
        manifestdata = getManifestTemplate('ntpd.pp')
        appendManifestFile('%s_ntpd.pp' % hostname,
                           manifestdata,
                           marker=marker)
