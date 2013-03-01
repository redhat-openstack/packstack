"""
Installs and configures Nagios
"""

import uuid
import logging

from packstack.installer import validators
from packstack.installer import basedefs, output_messages
from packstack.installer import utils

from packstack.modules.ospluginutils import gethostlist,\
                                            getManifestTemplate,\
                                            appendManifestFile

# Controller object will be initialized from main flow
controller = None

# Plugin name
PLUGIN_NAME = "OS-Nagios"
PLUGIN_NAME_COLORED = utils.color_text(PLUGIN_NAME, 'blue')

logging.debug("plugin %s loaded", __name__)

def initConfig(controllerObject):
    global controller
    controller = controllerObject
    logging.debug("Adding OpenStack Nagios configuration")
    paramsList = [
                  {"CMD_OPTION"      : "nagios-host",
                   "USAGE"           : "The IP address of the server on which to install the Nagios server",
                   "PROMPT"          : "Enter the IP address of the Nagios server",
                   "OPTION_LIST"     : [],
                   "VALIDATORS"      : [validators.validate_ssh],
                   "DEFAULT_VALUE"   : utils.get_localhost_ip(),
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_NAGIOS_HOST",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "nagios-passwd",
                   "USAGE"           : "The password of the nagiosadmin user on the Nagios server",
                   "PROMPT"          : "Enter the password for the nagiosadmin user",
                   "OPTION_LIST"     : [],
                   "VALIDATORS"      : [validators.validate_not_empty],
                   "DEFAULT_VALUE"   : uuid.uuid4().hex[:16],
                   "MASK_INPUT"      : True,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_NAGIOS_PW",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                 ]

    groupDict = { "GROUP_NAME"            : "NAGIOS",
                  "DESCRIPTION"           : "Nagios Config parameters",
                  "PRE_CONDITION"         : "CONFIG_NAGIOS_INSTALL",
                  "PRE_CONDITION_MATCH"   : "y",
                  "POST_CONDITION"        : False,
                  "POST_CONDITION_MATCH"  : True}

    controller.addGroup(groupDict, paramsList)


def initSequences(controller):
    conf = controller.CONF
    if conf['CONFIG_NAGIOS_INSTALL'] != 'y':
        return

    nagiossteps = [
             {'title': 'Adding Nagios server manifest entries', 'functions':[createmanifest]},
             {'title': 'Adding Nagios host manifest entries', 'functions':[createnrpemanifests]}
    ]
    controller.addSequence("Installing Nagios", [], [], nagiossteps)

def _serviceentry(**kwargs):
    s = 'define service {\n'
    keys = kwargs.keys()
    keys.sort()
    for key in keys:
        s += "\t%s\t%s\n"%(key, kwargs[key])
    s+= "\t}\n"
    return s

def _copy_script(**kwargs):
    # TODO : Replace all these shell templates with with python
    s = ('file{"/usr/lib64/nagios/plugins/%(name)s":'
        'mode => 755, owner => "nagios", seltype => "nagios_unconfined_plugin_exec_t",'
        'content => template("packstack/%(name)s.erb"),}\n'
        'nagios_command{"%(name)s": command_line => "/usr/lib64/nagios/plugins/%(name)s", }\n' % kwargs)
    return s

def createmanifest():
    manifest_entries = ''
    # I should be adding service entries with nagios_service but it appears to  be broken
    # http://projects.puppetlabs.com/issues/3420
    service_entries = ''
    for hostname in gethostlist(controller.CONF):
        manifest_entries += "nagios_host{'%s': address => '%s', use   => 'linux-server', }\n" % (hostname, hostname)

        service_entries += _serviceentry(name='load5-%s'%hostname, service_description='5 minute load average',
                                         host_name=hostname, check_command="check_nrpe!load5", use="generic-service",
                                         normal_check_interval='5')

        service_entries += _serviceentry(name='df_var-%s'%hostname,
                                         service_description='Percent disk space used on /var',
                                         host_name=hostname,
                                         check_command="check_nrpe!df_var", use="generic-service")

    manifest_entries += _copy_script(name="keystone-user-list")
    service_entries += _serviceentry(name='keystone-user-list',
        service_description='number of keystone users',
        host_name=controller.CONF['CONFIG_NAGIOS_HOST'],
        check_command="keystone-user-list", use="generic-service",
        normal_check_interval='5')

    if controller.CONF['CONFIG_GLANCE_INSTALL'] == 'y':
        manifest_entries += _copy_script(name="glance-index")
        service_entries += _serviceentry(name='glance-index',
            service_description='number of glance images',
            host_name=controller.CONF['CONFIG_NAGIOS_HOST'],
            check_command="glance-index", use="generic-service",
            normal_check_interval='5')

    if controller.CONF['CONFIG_NOVA_INSTALL'] == 'y':
        manifest_entries += _copy_script(name="nova-list")
        service_entries += _serviceentry(name='nova-list',
            service_description='number of nova vm instances',
            host_name=controller.CONF['CONFIG_NAGIOS_HOST'],
            check_command="nova-list", use="generic-service",
            normal_check_interval='5')

    if controller.CONF['CONFIG_CINDER_INSTALL'] == 'y':
        manifest_entries += _copy_script(name="cinder-list")
        service_entries += _serviceentry(name='cinder-list',
            service_description='number of cinder volumes',
            host_name=controller.CONF['CONFIG_NAGIOS_HOST'],
            check_command="cinder-list", use="generic-service",
            normal_check_interval='5')

    if controller.CONF['CONFIG_SWIFT_INSTALL'] == 'y':
        manifest_entries += _copy_script(name="swift-list")
        service_entries += _serviceentry(name='swift-list',
            service_description='number of swift containers',
            host_name=controller.CONF['CONFIG_NAGIOS_HOST'],
            check_command="swift-list", use="generic-service",
            normal_check_interval='5')

    manifest_entries+="file{'/etc/nagios/resource.d/nagios_service.cfg': \n" \
                      "ensure => present, mode => 644,\n" \
                      "content => '%s'}" % service_entries

    controller.CONF['CONFIG_NAGIOS_MANIFEST_CONFIG'] = manifest_entries

    manifestfile = "%s_nagios.pp" % controller.CONF['CONFIG_NAGIOS_HOST']
    manifestdata = getManifestTemplate("nagios_server.pp")
    appendManifestFile(manifestfile, manifestdata)

def createnrpemanifests():
    for hostname in gethostlist(controller.CONF):
        controller.CONF['CONFIG_NRPE_HOST'] = hostname
        manifestfile = "%s_nagios_nrpe.pp" % hostname
        manifestdata = getManifestTemplate("nagios_nrpe.pp")
        appendManifestFile(manifestfile, manifestdata)

    controller.MESSAGES.append("To use Nagios, browse to http://%s/nagios "
                               "username : nagiosadmin, password : %s" %
                               (controller.CONF['CONFIG_NAGIOS_HOST'],
                                controller.CONF['CONFIG_NAGIOS_PW']))
