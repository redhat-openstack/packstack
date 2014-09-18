"""
prepare server
"""

import os
import re
import uuid
import logging
import platform

from packstack.installer import basedefs
from packstack.installer import exceptions
from packstack.installer import utils
from packstack.installer import validators

from packstack.modules.common import filtered_hosts, is_all_in_one

# Controller object will be initialized from main flow
controller = None

# Plugin name
PLUGIN_NAME = "OS-SERVERPREPARE"
PLUGIN_NAME_COLORED = utils.color_text(PLUGIN_NAME, 'blue')

logging.debug("plugin %s loaded", __name__)

def initConfig(controllerObject):
    global controller
    controller = controllerObject
    logging.debug("Adding SERVERPREPARE KEY configuration")
    conf_params = {
            "SERVERPREPARE": [
                  {"CMD_OPTION"      : "use-epel",
                   "USAGE"           : "To subscribe each server to EPEL enter \"y\"",
                   "PROMPT"          : "To subscribe each server to EPEL enter \"y\"",
                   "OPTION_LIST"     : ["y", "n"],
                   "VALIDATORS"      : [validators.validate_options],
                   "DEFAULT_VALUE"   : "n",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_USE_EPEL",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },

                  {"CMD_OPTION"      : "additional-repo",
                   "USAGE"           : "A comma separated list of URLs to any additional yum repositories to install",
                   "PROMPT"          : "Enter a comma separated list of URLs to any additional yum repositories to install",
                   "OPTION_LIST"     : [],
                   "DEFAULT_VALUE"   : "",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_REPO",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False }],

            "RHEL": [
                  {"CMD_OPTION"      : "rh-username",
                   "USAGE"           : "To subscribe each server with Red Hat subscription manager, include this with CONFIG_RH_PW",
                   "PROMPT"          : "To subscribe each server to Red Hat enter a username here",
                   "OPTION_LIST"     : [],
                   "DEFAULT_VALUE"   : "",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_RH_USER",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },

                  {"CMD_OPTION"      : "rh-password",
                   "USAGE"           : "To subscribe each server with Red Hat subscription manager, include this with CONFIG_RH_USER",
                   "PROMPT"          : "To subscribe each server to Red Hat enter your password here",
                   "OPTION_LIST"     : [],
                   "DEFAULT_VALUE"   : "",
                   "MASK_INPUT"      : True,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_RH_PW",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },

                  {"CMD_OPTION"      : "rh-beta-repo",
                   "USAGE"           : "To subscribe each server to Red Hat Enterprise Linux 6 Server Beta channel (only needed for Preview versions of RHOS) enter \"y\"",
                   "PROMPT"          : "To subscribe each server to Red Hat Enterprise Linux 6 Server Beta channel (only needed for Preview versions of RHOS) enter \"y\"",
                   "OPTION_LIST"     : ["y", "n"],
                   "VALIDATORS"      : [validators.validate_options],
                   "DEFAULT_VALUE"   : "n",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_RH_BETA_REPO",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },

                  {"CMD_OPTION"      : "rhn-satellite-server",
                   "USAGE"           : ("To subscribe each server with RHN Satellite,"
                                        "fill Satellite's URL here. Note that either "
                                        "satellite's username/password or activation "
                                        "key has to be provided"),
                   "PROMPT"          : ("To subscribe each server with RHN Satellite "
                                        "enter RHN Satellite server URL"),
                   "OPTION_LIST"     : [],
                   "DEFAULT_VALUE"   : "",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": False,
                   "CONF_NAME"       : "CONFIG_SATELLITE_URL",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False }],

            "SATELLITE": [
                  {"CMD_OPTION"      : "rhn-satellite-username",
                   "USAGE"           : "Username to access RHN Satellite",
                   "PROMPT"          : ("Enter RHN Satellite username or leave plain "
                                        "if you will use activation key instead"),
                   "OPTION_LIST"     : [],
                   "DEFAULT_VALUE"   : "",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_SATELLITE_USER",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },

                  {"CMD_OPTION"      : "rhn-satellite-password",
                   "USAGE"           : "Password to access RHN Satellite",
                   "PROMPT"          : ("Enter RHN Satellite password or leave plain "
                                        "if you will use activation key instead"),
                   "OPTION_LIST"     : [],
                   "DEFAULT_VALUE"   : "",
                   "MASK_INPUT"      : True,
                   "LOOSE_VALIDATION": False,
                   "CONF_NAME"       : "CONFIG_SATELLITE_PW",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },

                  {"CMD_OPTION"      : "rhn-satellite-activation-key",
                   "USAGE"           : "Activation key for subscription to RHN Satellite",
                   "PROMPT"          : ("Enter RHN Satellite activation key or leave plain "
                                        "if you used username/password instead"),
                   "OPTION_LIST"     : [],
                   "DEFAULT_VALUE"   : "",
                   "MASK_INPUT"      : True,
                   "LOOSE_VALIDATION": False,
                   "CONF_NAME"       : "CONFIG_SATELLITE_AKEY",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },

                  {"CMD_OPTION"      : "rhn-satellite-cacert",
                   "USAGE"           : "Specify a path or URL to a SSL CA certificate to use",
                   "PROMPT"          : "Specify a path or URL to a SSL CA certificate to use",
                   "OPTION_LIST"     : [],
                   "DEFAULT_VALUE"   : "",
                   "MASK_INPUT"      : True,
                   "LOOSE_VALIDATION": False,
                   "CONF_NAME"       : "CONFIG_SATELLITE_CACERT",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },

                  {"CMD_OPTION"      : "rhn-satellite-profile",
                   "USAGE"           : ("If required specify the profile name that should "
                                        "be used as an identifier for the system in RHN "
                                        "Satellite"),
                   "PROMPT"          : ("If required specify the profile name that should "
                                        "be used as an identifier for the system in RHN "
                                        "Satellite"),
                   "OPTION_LIST"     : [],
                   "DEFAULT_VALUE"   : "",
                   "MASK_INPUT"      : True,
                   "LOOSE_VALIDATION": False,
                   "CONF_NAME"       : "CONFIG_SATELLITE_PROFILE",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },

                  {"CMD_OPTION"      : "rhn-satellite-flags",
                   "USAGE"           : ("Comma separated list of flags passed to rhnreg_ks. Valid "
                                        "flags are: novirtinfo, norhnsd, nopackages"),
                   "PROMPT"          : "Enter comma separated list of flags passed to rhnreg_ks",
                   "OPTION_LIST"     : ['novirtinfo', 'norhnsd', 'nopackages'],
                   "VALIDATORS"      : [validators.validate_multi_options],
                   "DEFAULT_VALUE"   : "",
                   "MASK_INPUT"      : True,
                   "LOOSE_VALIDATION": False,
                   "CONF_NAME"       : "CONFIG_SATELLITE_FLAGS",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },

                  {"CMD_OPTION"      : "rhn-satellite-proxy-host",
                   "USAGE"           : "Specify a HTTP proxy to use with RHN Satellite",
                   "PROMPT"          : "Specify a HTTP proxy to use with RHN Satellite",
                   "OPTION_LIST"     : [],
                   "DEFAULT_VALUE"   : "",
                   "MASK_INPUT"      : True,
                   "LOOSE_VALIDATION": False,
                   "CONF_NAME"       : "CONFIG_SATELLITE_PROXY",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False }],

            "SATELLITE_PROXY": [
                  {"CMD_OPTION"      : "rhn-satellite-proxy-username",
                   "USAGE"           : "Specify a username to use with an authenticated HTTP proxy",
                   "PROMPT"          : "Specify a username to use with an authenticated HTTP proxy",
                   "OPTION_LIST"     : [],
                   "DEFAULT_VALUE"   : "",
                   "MASK_INPUT"      : True,
                   "LOOSE_VALIDATION": False,
                   "CONF_NAME"       : "CONFIG_SATELLITE_PROXY_USER",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },

                  {"CMD_OPTION"      : "rhn-satellite-proxy-password",
                   "USAGE"           : "Specify a password to use with an authenticated HTTP proxy.",
                   "PROMPT"          : "Specify a password to use with an authenticated HTTP proxy.",
                   "OPTION_LIST"     : [],
                   "DEFAULT_VALUE"   : "",
                   "MASK_INPUT"      : True,
                   "LOOSE_VALIDATION": False,
                   "CONF_NAME"       : "CONFIG_SATELLITE_PROXY_PW",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False }]}

    def filled_satellite(config):
        return bool(config.get('CONFIG_SATELLITE_URL'))

    def filled_satellite_proxy(config):
        return bool(config.get('CONFIG_SATELLITE_PROXY'))

    conf_groups = [
             {"GROUP_NAME"            : "SERVERPREPARE",
              "DESCRIPTION"           : "Server Prepare Configs ",
              "PRE_CONDITION"         : lambda x: 'yes',
              "PRE_CONDITION_MATCH"   : "yes",
              "POST_CONDITION"        : False,
              "POST_CONDITION_MATCH"  : True},
        ]

    if ((is_all_in_one(controller.CONF) and is_rhel()) or
        not is_all_in_one(controller.CONF)):
        conf_groups.append({"GROUP_NAME"            : "RHEL",
                            "DESCRIPTION"           : "RHEL config",
                            "PRE_CONDITION"         : lambda x: 'yes',
                            "PRE_CONDITION_MATCH"   : "yes",
                            "POST_CONDITION"        : False,
                            "POST_CONDITION_MATCH"  : True})

        conf_groups.append({"GROUP_NAME"            : "SATELLITE",
                            "DESCRIPTION"           : "RHN Satellite config",
                            "PRE_CONDITION"         : filled_satellite,
                            "PRE_CONDITION_MATCH"   : True,
                            "POST_CONDITION"        : False,
                            "POST_CONDITION_MATCH"  : True})

        conf_groups.append({"GROUP_NAME"            : "SATELLITE_PROXY",
                            "DESCRIPTION"           : "RHN Satellite proxy config",
                            "PRE_CONDITION"         : filled_satellite_proxy,
                            "PRE_CONDITION_MATCH"   : True,
                            "POST_CONDITION"        : False,
                            "POST_CONDITION_MATCH"  : True})

    for group in conf_groups:
        paramList = conf_params[group["GROUP_NAME"]]
        controller.addGroup(group, paramList)


def is_rhel():
    return 'Red Hat Enterprise Linux' in platform.linux_distribution()[0]


def run_rhn_reg(host, server_url, username=None, password=None,
                cacert=None, activation_key=None, profile_name=None,
                proxy_host=None, proxy_user=None, proxy_pass=None,
                flags=None):
    """
    Registers given host to given RHN Satellite server. To successfully
    register either activation_key or username/password is required.
    """
    logging.debug('Setting RHN Satellite server: %s.' % locals())

    mask = []
    cmd = ['/usr/sbin/rhnreg_ks']
    server = utils.ScriptRunner(host)

    # check satellite server url
    server_url = server_url.rstrip('/').endswith('/XMLRPC') \
                    and server_url \
                    or '%s/XMLRPC' % server_url
    cmd.extend(['--serverUrl', server_url])

    if activation_key:
        cmd.extend(['--activationkey', activation_key])
    elif username:
        cmd.extend(['--username', username])
        if password:
            cmd.extend(['--password', password])
            mask.append(password)
    else:
        raise exceptions.InstallError('Either RHN Satellite activation '
                                      'key or username/password must '
                                      'be provided.')

    if cacert:
        # use and if required download given certificate
        location = "/etc/sysconfig/rhn/%s" % os.path.basename(cacert)
        if not os.path.isfile(location):
            logging.debug('Downloading cacert from %s.' % server_url)
            wget_cmd = ('ls %(location)s &> /dev/null && echo -n "" || '
                        'wget -nd --no-check-certificate --timeout=30 '
                        '--tries=3 -O "%(location)s" "%(cacert)s"' %
                        locals())
            server.append(wget_cmd)
        cmd.extend(['--sslCACert', location])

    if profile_name:
        cmd.extend(['--profilename', profile_name])
    if proxy_host:
        cmd.extend(['--proxy', proxy_host])
        if proxy_user:
            cmd.extend(['--proxyUser', proxy_user])
            if proxy_pass:
                cmd.extend(['--proxyPassword', proxy_pass])
                mask.append(proxy_pass)

    flags = flags or []
    flags.append('force')
    for i in flags:
        cmd.append('--%s' % i)

    server.append(' '.join(cmd))
    server.append('yum clean metadata')
    server.execute(mask_list=mask)


def run_rhsm_reg(host, username, password, beta):
    """
    Registers given host to Red Hat Repositories via subscription manager.
    """
    server = utils.ScriptRunner(host)

    # register host
    cmd = ('subscription-manager register --username=\"%s\" '
                            '--password=\"%s\" --autosubscribe || true')
    server.append(cmd % (username, password.replace('"','\\"')))

    # subscribe to required channel
    cmd = ('subscription-manager list --consumed | grep -i openstack || '
           'subscription-manager subscribe --pool %s')
    pool = ("$(subscription-manager list --available | "
            "grep -e 'Red Hat OpenStack' -m 1 -A 2 | grep 'Pool Id' | "
            "awk '{print $3}')")
    server.append(cmd % pool)
    server.append("subscription-manager repos --enable rhel-6-server-optional-rpms")

    server.append("yum clean all")
    server.append("rpm -q --whatprovides yum-utils || yum install -y yum-utils")
    if beta:
        server.append("yum-config-manager --enable rhel-6-server-beta-rpms")
    server.append("yum clean metadata")
    server.execute(mask_list=[password])


def manage_epel(host, config):
    """
    Installs and/or enables EPEL repo if it is required or disables it if it
    is not required.
    """
    if config['HOST_DETAILS'][host]['os'] in ('Fedora', 'Unknown'):
        return

    mirrors = ('https://mirrors.fedoraproject.org/metalink?repo=epel-6&'
               'arch=$basearch')
    server = utils.ScriptRunner(host)
    if config['CONFIG_USE_EPEL'] == 'y':
        server.append('REPOFILE=$(mktemp)')
        server.append('cat /etc/yum.conf > $REPOFILE')
        server.append("echo -e '[packstack-epel]\nname=packstack-epel\n"
                      "enabled=1\nmirrorlist=%(mirrors)s' >> $REPOFILE"
                      % locals())
        server.append('( rpm -q --whatprovides epel-release ||'
                      ' yum install -y --nogpg -c $REPOFILE epel-release ) '
                      '|| true')
        server.append('rm -rf $REPOFILE')
        try:
            server.execute()
        except exceptions.ScriptRuntimeError as ex:
            msg = 'Failed to set EPEL repo on host %s:\n%s' % (host, ex)
            raise exceptions.ScriptRuntimeError(msg)

    # if there's an epel repo explicitly enables or disables it
    # according to: CONFIG_USE_EPEL
    if config['CONFIG_USE_EPEL'] == 'y':
        cmd = 'enable'
        enabled = '(1|True)'
    else:
        cmd = 'disable'
        enabled = '(0|False)'

    server.clear()
    server.append('yum-config-manager --%(cmd)s epel' % locals())
    rc, out = server.execute()

    # yum-config-manager returns 0 always, but returns current setup if succeeds
    match = re.search('enabled\s*\=\s*%(enabled)s' % locals(), out)
    if match:
        return
    msg = 'Failed to set EPEL repo on host %s:\n'
    if cmd == 'enable':
        # fail in case user wants to have EPEL enabled
        msg += ('RPM file seems to be installed, but appropriate repo file is '
                'probably missing in /etc/yum.repos.d/')
        raise exceptions.ScriptRuntimeError(msg % host)
    else:
        # just warn in case disabling failed which might happen when EPEL repo
        # is not installed at all
        msg += 'This is OK in case you don\'t want EPEL installed and enabled.'
        # TO-DO: fill logger name when logging will be refactored.
        logger = logging.getLogger()
        logger.warn(msg % host)



def manage_rdo(host, config):
    """
    Installs and enables RDO repo on host in case it is installed locally.
    """
    try:
        cmd = "rpm -q rdo-release --qf='%{version}-%{release}.%{arch}\n'"
        rc, out = utils.execute(cmd, use_shell=True)
    except exceptions.ExecuteRuntimeError:
        # RDO repo is not installed, so we don't need to continue
        return
    match = re.match(r'^(?P<version>\w+)\-(?P<release>\d+\.[\d\w]+)\n', out)
    version, release = match.group('version'), match.group('release')
    rdo_url = ("http://rdo.fedorapeople.org/openstack/openstack-%(version)s/"
               "rdo-release-%(version)s-%(release)s.rpm" % locals())

    server = utils.ScriptRunner(host)
    server.append("(rpm -q 'rdo-release-%(version)s' ||"
                  " yum install -y --nogpg %(rdo_url)s) || true"
                  % locals())
    try:
        server.execute()
    except exceptions.ScriptRuntimeError as ex:
        msg = 'Failed to set RDO repo on host %s:\n%s' % (host, ex)
        raise exceptions.ScriptRuntimeError(msg)

    reponame = 'openstack-%s' % version
    server.clear()
    server.append('yum-config-manager --enable %(reponame)s' % locals())
    # yum-config-manager returns 0 always, but returns current setup if succeeds
    rc, out = server.execute()
    match = re.search('enabled\s*=\s*(1|True)', out)
    if not match:
        msg = ('Failed to set RDO repo on host %s:\nRPM file seems to be '
               'installed, but appropriate repo file is probably missing '
               'in /etc/yum.repos.d/' % host)
        raise exceptions.ScriptRuntimeError(msg)


def initSequences(controller):
    preparesteps = [
             {'title': 'Preparing servers', 'functions':[serverprep]}
    ]
    controller.addSequence("Preparing servers", [], [], preparesteps)


def serverprep(config):
    rh_username = None
    sat_url = None
    if is_rhel():
        rh_username = config["CONFIG_RH_USER"].strip()
        rh_password = config["CONFIG_RH_PW"].strip()

        sat_registered = set()

        sat_url = config["CONFIG_SATELLITE_URL"].strip()
        if sat_url:
            flag_list = config["CONFIG_SATELLITE_FLAGS"].split(',')
            sat_flags = [i.strip() for i in flag_list if i.strip()]
            sat_proxy_user = config.get("CONFIG_SATELLITE_PROXY_USER", '')
            sat_proxy_pass = config.get("CONFIG_SATELLITE_PROXY_PW", '')
            sat_args = {'username': config["CONFIG_SATELLITE_USER"].strip(),
                        'password': config["CONFIG_SATELLITE_PW"].strip(),
                        'cacert': config["CONFIG_SATELLITE_CACERT"].strip(),
                        'activation_key': config["CONFIG_SATELLITE_AKEY"].strip(),
                        'profile_name': config["CONFIG_SATELLITE_PROFILE"].strip(),
                        'proxy_host': config["CONFIG_SATELLITE_PROXY"].strip(),
                        'proxy_user': sat_proxy_user.strip(),
                        'proxy_pass': sat_proxy_pass.strip(),
                        'flags': sat_flags}

    for hostname in filtered_hosts(config):
        # Subscribe to Red Hat Repositories if configured
        if rh_username:
            run_rhsm_reg(hostname, rh_username, rh_password,
                         config["CONFIG_RH_BETA_REPO"] == 'y')

        # Subscribe to RHN Satellite if configured
        if sat_url and hostname not in sat_registered:
            run_rhn_reg(hostname, sat_url, **sat_args)
            sat_registered.add(hostname)

        server = utils.ScriptRunner(hostname)
        server.append('rpm -q --whatprovides yum-utils || '
                      'yum install -y yum-utils')


        # Installing rhos-log-collector and sos-plugins-openstack if
        # these rpms are available from yum.
        sos_rpms = ' '.join(('rhos-log-collector',
                            'sos',
                            'sos-plugins-openstack'))

        server.append('yum list available rhos-log-collector && '
                      'yum -y install %s || '
                      'echo "no rhos-log-collector available"' % sos_rpms)
        server.execute()

        # enable or disable EPEL according to configuration
        manage_epel(hostname, config)
        # enable RDO if it is installed locally
        manage_rdo(hostname, config)

        reponame = 'rhel-server-ost-6-4-rpms'
        server.clear()
        server.append('yum install -y yum-plugin-priorities || true')
        server.append('rpm -q epel-release && yum-config-manager '
                        '--setopt="%(reponame)s.priority=1" '
                        '--save %(reponame)s' % locals())

        # Add yum repositories if configured
        CONFIG_REPO = config["CONFIG_REPO"].strip()
        if CONFIG_REPO:
            for i, repourl in enumerate(CONFIG_REPO.split(',')):
                reponame = 'packstack_%d' % i
                server.append('echo "[%(reponame)s]\nname=%(reponame)s\n'
                                    'baseurl=%(repourl)s\nenabled=1\n'
                                    'priority=1\ngpgcheck=0"'
                              ' > /etc/yum.repos.d/%(reponame)s.repo'
                              % locals())

        server.append("yum clean metadata")
        server.execute()
