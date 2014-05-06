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

from packstack.modules.common import filtered_hosts
from packstack.modules.ospluginutils import (getManifestTemplate,
                                             appendManifestFile)


# Controller object will be initialized from main flow
controller = None

# Plugin name
PLUGIN_NAME = "OS-PRESCRIPT"

logging.debug("plugin %s loaded", __name__)


def initConfig(controllerObject):
    global controller
    controller = controllerObject

    paramsList = [{"CMD_OPTION"      : "ssh-public-key",
                   "USAGE"           : "Path to a Public key to install on servers. If a usable key has not been installed on the remote servers the user will be prompted for a password and this key will be installed so the password will not be required again",
                   "PROMPT"          : "Enter the path to your ssh Public key to install on servers",
                   "OPTION_LIST"     : [],
                   "VALIDATORS"      : [validators.validate_file,
                                        validators.validate_sshkey],
                   "PROCESSORS"      : [processors.process_ssh_key],
                   "DEFAULT_VALUE"   : (glob.glob(os.path.join(os.environ["HOME"], ".ssh/*.pub"))+[""])[0],
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": False,
                   "CONF_NAME"       : "CONFIG_SSH_KEY",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "os-mysql-install",
                   "USAGE"           : "Set to 'y' if you would like Packstack to install MySQL",
                   "PROMPT"          : "Should Packstack install MySQL DB",
                   "OPTION_LIST"     : ["y", "n"],
                   "VALIDATORS"      : [validators.validate_options],
                   "DEFAULT_VALUE"   : "y",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": False,
                   "CONF_NAME"       : "CONFIG_MYSQL_INSTALL",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "os-glance-install",
                   "USAGE"           : "Set to 'y' if you would like Packstack to install OpenStack Image Service (Glance)",
                   "PROMPT"          : "Should Packstack install OpenStack Image Service (Glance)",
                   "OPTION_LIST"     : ["y", "n"],
                   "VALIDATORS"      : [validators.validate_options],
                   "DEFAULT_VALUE"   : "y",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": False,
                   "CONF_NAME"       : "CONFIG_GLANCE_INSTALL",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "os-cinder-install",
                   "USAGE"           : "Set to 'y' if you would like Packstack to install OpenStack Block Storage (Cinder)",
                   "PROMPT"          : "Should Packstack install OpenStack Block Storage (Cinder) service",
                   "OPTION_LIST"     : ["y", "n"],
                   "VALIDATORS"      : [validators.validate_options],
                   "DEFAULT_VALUE"   : "y",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": False,
                   "CONF_NAME"       : "CONFIG_CINDER_INSTALL",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "os-nova-install",
                   "USAGE"           : "Set to 'y' if you would like Packstack to install OpenStack Compute (Nova)",
                   "PROMPT"          : "Should Packstack install OpenStack Compute (Nova) service",
                   "OPTION_LIST"     : ["y", "n"],
                   "VALIDATORS"      : [validators.validate_options],
                   "DEFAULT_VALUE"   : "y",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": False,
                   "CONF_NAME"       : "CONFIG_NOVA_INSTALL",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "os-neutron-install",
                   "USAGE"           : "Set to 'y' if you would like Packstack to install OpenStack Networking (Neutron)",
                   "PROMPT"          : "Should Packstack install OpenStack Networking (Neutron) service",
                   "OPTION_LIST"     : ["y", "n"],
                   "VALIDATORS"      : [validators.validate_options],
                   "DEFAULT_VALUE"   : "y",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": False,
                   "CONF_NAME"       : "CONFIG_NEUTRON_INSTALL",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "os-horizon-install",
                   "USAGE"           : "Set to 'y' if you would like Packstack to install OpenStack Dashboard (Horizon)",
                   "PROMPT"          : "Should Packstack install OpenStack Dashboard (Horizon)",
                   "OPTION_LIST"     : ["y", "n"],
                   "VALIDATORS"      : [validators.validate_options],
                   "DEFAULT_VALUE"   : "y",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": False,
                   "CONF_NAME"       : "CONFIG_HORIZON_INSTALL",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "os-swift-install",
                   "USAGE"           : "Set to 'y' if you would like Packstack to install OpenStack Object Storage (Swift)",
                   "PROMPT"          : "Should Packstack install OpenStack Object Storage (Swift)",
                   "OPTION_LIST"     : ["y", "n"],
                   "VALIDATORS"      : [validators.validate_options],
                   "DEFAULT_VALUE"   : "y",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": False,
                   "CONF_NAME"       : "CONFIG_SWIFT_INSTALL",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "os-ceilometer-install",
                   "USAGE"           : "Set to 'y' if you would like Packstack to install OpenStack Metering (Ceilometer)",
                   "PROMPT"          : "Should Packstack install OpenStack Metering (Ceilometer)",
                   "OPTION_LIST"     : ["y", "n"],
                   "VALIDATORS"      : [validators.validate_options],
                   "DEFAULT_VALUE"   : "y",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": False,
                   "CONF_NAME"       : "CONFIG_CEILOMETER_INSTALL",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "os-heat-install",
                   "USAGE"           : "Set to 'y' if you would like Packstack to install OpenStack Orchestration (Heat)",
                   "PROMPT"          : "Should Packstack install OpenStack Orchestration (Heat)",
                   "OPTION_LIST"     : ["y", "n"],
                   "VALIDATORS"      : [validators.validate_options],
                   "DEFAULT_VALUE"   : "n",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": False,
                   "CONF_NAME"       : "CONFIG_HEAT_INSTALL",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "os-client-install",
                   "USAGE"           : "Set to 'y' if you would like Packstack to install the OpenStack Client packages. An admin \"rc\" file will also be installed",
                   "PROMPT"          : "Should Packstack install OpenStack client tools",
                   "OPTION_LIST"     : ["y", "n"],
                   "VALIDATORS"      : [validators.validate_options],
                   "DEFAULT_VALUE"   : "y",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": False,
                   "CONF_NAME"       : "CONFIG_CLIENT_INSTALL",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "ntp-servers",
                   "USAGE"           : "Comma separated list of NTP servers. Leave plain if Packstack should not install ntpd on instances.",
                   "PROMPT"          : "Enter a comma separated list of NTP server(s). Leave plain if Packstack should not install ntpd on instances.",
                   "OPTION_LIST"     : [],
                   "DEFAULT_VALUE"   : '',
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": False,
                   "CONF_NAME"       : "CONFIG_NTP_SERVERS",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "nagios-install",
                   "USAGE"           : "Set to 'y' if you would like Packstack to install Nagios to monitor OpenStack hosts",
                   "PROMPT"          : "Should Packstack install Nagios to monitor OpenStack hosts",
                   "OPTION_LIST"     : ["y", "n"],
                   "VALIDATORS"      : [validators.validate_options],
                   "DEFAULT_VALUE"   : 'y',
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": False,
                   "CONF_NAME"       : "CONFIG_NAGIOS_INSTALL",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "exclude-servers",
                   "USAGE"           : "Comma separated list of servers to be excluded from installation in case you are running Packstack the second time with the same answer file and don't want Packstack to touch these servers. Leave plain if you don't need to exclude any server.",
                   "PROMPT"          : "Enter a comma separated list of server(s) to be excluded. Leave plain if you don't need to exclude any server.",
                   "OPTION_LIST"     : [],
                   "DEFAULT_VALUE"   : '',
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": False,
                   "CONF_NAME"       : "EXCLUDE_SERVERS",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "os-debug-mode",
                   "USAGE"           : ("Set to 'y' if you want to run "
                                        "OpenStack services in debug mode. "
                                        "Otherwise set to 'n'."),
                   "PROMPT"          : ("Do you want to run OpenStack services"
                                        " in debug mode"),
                   "OPTION_LIST"     : ["y", "n"],
                   "DEFAULT_VALUE"   : "n",
                   "VALIDATORS"      : [validators.validate_options],
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": False,
                   "CONF_NAME"       : "CONFIG_DEBUG_MODE",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "os-vmware",
                   "USAGE"           : ("Set to 'y' if you want to use "
                                        "VMware vCenter as hypervisor and storage"
                                        "Otherwise set to 'n'."),
                   "PROMPT"          : ("Do you want to use VMware vCenter as"
                                        " hypervisor and datastore"),
                   "OPTION_LIST"     : ["y","n"],
                   "DEFAULT_VALUE"   : "n",
                   "VALIDATORS"      : [validators.validate_options],
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": False,
                   "CONF_NAME"       : "CONFIG_VMWARE_BACKEND",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                 ]
    groupDict = { "GROUP_NAME"            : "GLOBAL",
                  "DESCRIPTION"           : "Global Options",
                  "PRE_CONDITION"         : lambda x: 'yes',
                  "PRE_CONDITION_MATCH"   : "yes",
                  "POST_CONDITION"        : False,
                  "POST_CONDITION_MATCH"  : True}
    controller.addGroup(groupDict, paramsList)

    def use_vcenter(config):
         return (config['CONFIG_NOVA_INSTALL'] == 'y' and
                config['CONFIG_VMWARE_BACKEND'] == 'y')

    paramsList = [
                  {"CMD_OPTION"      : "vcenter-host",
                   "USAGE"           : ("The IP address of the VMware vCenter server"),
                   "PROMPT"          : ("Enter the IP address of the VMware vCenter server to use with Nova"),
                   "OPTION_LIST"     : [],
                   "VALIDATORS"      : [validators.validate_ip],
                   "DEFAULT_VALUE"   : "",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_VCENTER_HOST",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "vcenter-username",
                   "USAGE"           : ("The username to authenticate to VMware vCenter server"),
                   "PROMPT"          : ("Enter the username to authenticate on VMware vCenter server"),
                   "DEFAULT_VALUE"   : "",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_VCENTER_USER",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False,},
                  {"CMD_OPTION"      : "vcenter-password",
                   "USAGE"           : ("The password to authenticate to VMware vCenter server"),
                   "PROMPT"          : ("Enter the password to authenticate on VMware vCenter server"),
                   "DEFAULT_VALUE"   : "",
                   "MASK_INPUT"      : True,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_VCENTER_PASSWORD",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False,},
                  {"CMD_OPTION"      : "vcenter-cluster",
                   "USAGE"           : ("The name of the vCenter cluster"),
                   "PROMPT"          : ("Enter the name of the vCenter datastore"),
                   "DEFAULT_VALUE"   : "",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_VCENTER_CLUSTER_NAME",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False,},
                  ]

    groupDict = {"GROUP_NAME"            : "VMWARE",
                  "DESCRIPTION"           : "vCenter Config Parameters",
                  "PRE_CONDITION"         : use_vcenter,
                  "PRE_CONDITION_MATCH"   : True,
                  "POST_CONDITION"        : False,
                  "POST_CONDITION_MATCH"  : True}

    controller.addGroup(groupDict, paramsList)

def initSequences(controller):
    prescript_steps = [
        {'title': 'Setting up ssh keys',
            'functions':[install_keys]},
        {'title': 'Discovering hosts\' details',
            'functions': [discover]},
        {'title': 'Adding pre install manifest entries',
            'functions':[create_manifest]},
    ]

    if controller.CONF['CONFIG_NTP_SERVERS']:
        prescript_steps.append({
            'title': 'Installing time synchronization via NTP',
            'functions': [create_ntp_manifest],
        })
    else:
        controller.MESSAGES.append('Time synchronization installation '
                                   'was skipped. Please note that '
                                   'unsynchronized time on server '
                                   'instances might be problem for '
                                   'some OpenStack components.')
    controller.addSequence("Running pre install scripts", [], [],
                           prescript_steps)


def install_keys(config):
    with open(config["CONFIG_SSH_KEY"]) as fp:
        sshkeydata = fp.read().strip()
    for hostname in filtered_hosts(config):
        if '/' in hostname:
            hostname = hostname.split('/')[0]
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


def discover(config):
    """
    Discovers details about hosts.
    """
    # TODO: Once Controller is refactored, move this function to it (facter can
    #       be used for that too).
    details = {}
    release_regexp = re.compile(r'^(?P<OS>.*) release (?P<release>[\d\.]*)')
    for host in filtered_hosts(config):
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


def create_manifest(config):
    key = 'CONFIG_DEBUG_MODE'
    config[key] = config[key] == 'y' and 'true' or 'false'

    for hostname in filtered_hosts(config):
        manifestfile = "%s_prescript.pp" % hostname
        manifestdata = getManifestTemplate("prescript.pp")
        appendManifestFile(manifestfile, manifestdata)


def create_ntp_manifest(config):
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
