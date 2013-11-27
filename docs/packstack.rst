==============
Packstack
==============

SYNOPSIS
========

  packstack [options]

DESCRIPTION
===========
  Packstack is a utility that uses uses puppet modules to install OpenStack. It can be used to install each openstack service on separate servers, all on one server or any combination of these. There are 3 ways that Packstack can be run.
- packstack
- packstack [options]
- packstack --gen-answer-file=<file>  / packstack --answer-file=<file>

  The third option allows the user to generate a default answer file, edit the default options and finally run Packstack a second time using this answer file. This is the easiest way to run Packstack and the one that will be documented here. When <file> is created the OPTIONS below will be contained and can be edited by the user.

OPTIONS
=======

Global Options
--------------

**CONFIG_GLANCE_INSTALL**      : Set to 'y' if you would like Packstack to install Glance ['y', 'n'].

**CONFIG_CINDER_INSTALL**      : Set to 'y' if you would like Packstack to install Cinder ['y', 'n'].

**CONFIG_NOVA_INSTALL**        : Set to 'y' if you would like Packstack to install Nova ['y', 'n'].

**CONFIG_HORIZON_INSTALL**     : Set to 'y' if you would like Packstack to install Horizon ['y', 'n'].

**CONFIG_SWIFT_INSTALL**       : Set to 'y' if you would like Packstack to install Swift ['y', 'n'].

**CONFIG_CLIENT_INSTALL**      : Set to 'y' if you would like Packstack to install the OpenStack Client packages. An admin "rc" file will also be installed ['y', 'n'].

**CONFIG_NTP_SERVERS**         : Comma separated list of NTP servers. Leave plain if Packstack should not install ntpd on instances..

**CONFIG_NAGIOS_INSTALL**      : Set to 'y' if you would like Packstack to install Nagios to monitor openstack hosts ['y', 'n'].

**CONFIG_CEILOMETER_INSTALL** : Set to 'y' if you would like Packstack to install OpenStack Metering (Ceilometer).

**CONFIG_HEAT_INSTALL**       : Set to 'y' if you would like Packstack to install OpenStack Orchestration (Heat).

**CONFIG_NEUTRON_INSTALL**    : Set to 'y' if you would like Packstack to install OpenStack Networking (Neutron).

**CONFIG_MYSQL_INSTALL**      : Set to 'y' if you would like Packstack to install MySQL.


SSH Configs
------------

**CONFIG_SSH_KEY**             : Path to a Public key to install on servers. If a usable key has not been installed on the remote servers the user will be prompted for a password and this key will be installed so the password will not be required again.

MySQL Config parameters
-----------------------

**CONFIG_MYSQL_HOST**          : The IP address of the server on which to install MySQL.

**CONFIG_MYSQL_USER**          : Username for the MySQL admin user.

**CONFIG_MYSQL_PW**            : Password for the MySQL admin user.

QPID Config parameters
----------------------

**CONFIG_QPID_HOST**            : The IP address of the server on which to install the QPID service.

**CONFIG_QPID_ENABLE_SSL**      : Enable SSL for the QPID service.

**CONFIG_QPID_NSS_CERTDB_PW**   : The password for the NSS certificate database of the QPID service.

**CONFIG_QPID_SSL_PORT**        : The port in which the QPID service listens to SSL connections.

**CONFIG_QPID_SSL_CERT_FILE**   : The filename of the certificate that the QPID service is going to use.

**CONFIG_QPID_SSL_KEY_FILE**    : The filename of the private key that the QPID service is going to use.

**CONFIG_QPID_SSL_SELF_SIGNED** : Auto Generates self signed SSL certificate and key.

Keystone Config parameters
--------------------------

**CONFIG_KEYSTONE_HOST**       : The IP address of the server on which to install Keystone.

**CONFIG_KEYSTONE_DB_PW**      : The password to use for the Keystone to access DB.

**CONFIG_KEYSTONE_ADMIN_TOKEN** : The token to use for the Keystone service api.

**CONFIG_KEYSTONE_ADMIN_PW**   : The password to use for the Keystone admin user.

**CONFIG_KEYSTONE_DEMO_PW**    : The password to use for the Keystone demo user

**CONFIG_KEYSTONE_TOKEN_FORMAT**    : Kestone token format. Use either UUID or PKI

Glance Config parameters
------------------------

**CONFIG_GLANCE_HOST**         : The IP address of the server on which to install Glance.

**CONFIG_GLANCE_DB_PW**        : The password to use for the Glance to access DB.

**CONFIG_GLANCE_KS_PW**        : The password to use for the Glance to authenticate with Keystone.

Cinder Config parameters
------------------------

**CONFIG_CINDER_HOST**         : The IP address of the server on which to install Cinder.

**CONFIG_CINDER_DB_PW**        : The password to use for the Cinder to access DB.

**CONFIG_CINDER_KS_PW**        : The password to use for the Cinder to authenticate with Keystone.

**CONFIG_CINDER_BACKEND**      : The Cinder backend to use ['lvm', 'gluster', 'nfs'].

Cinder volume create Config parameters
--------------------------------------

**CONFIG_CINDER_VOLUMES_CREATE** : Create Cinder's volumes group ['y', 'n'].

Cinder volume size Config parameters
------------------------------------

**CONFIG_CINDER_VOLUMES_SIZE** : Cinder's volumes group size.

Cinder gluster Config parameters
--------------------------------

**CONFIG_CINDER_GLUSTER_MOUNTS** : A single or comma separated list of gluster volume shares.

Cinder NFS Config parameters
----------------------------

**CONFIG_CINDER_NFS_MOUNTS**   : A single or comma seprated list of NFS exports to mount.

Nova Options
------------

**CONFIG_NOVA_API_HOST**       : The IP address of the server on which to install the Nova API service.

**CONFIG_NOVA_CERT_HOST**      : The IP address of the server on which to install the Nova Cert service.

**CONFIG_NOVA_VNCPROXY_HOST**  : The IP address of the server on which to install the Nova VNC proxy.

**CONFIG_NOVA_COMPUTE_HOSTS**  : A comma separated list of IP addresses on which to install the Nova Compute services.

**CONFIG_NOVA_COMPUTE_PRIVIF** : Private interface for Flat DHCP on the Nova compute servers.

**CONFIG_NOVA_NETWORK_HOSTS**  : List of IP address of the servers on which to install the Nova Network service.

**CONFIG_NOVA_DB_PW**          : The password to use for the Nova to access DB.

**CONFIG_NOVA_KS_PW**          : The password to use for the Nova to authenticate with Keystone.

**CONFIG_NOVA_NETWORK_PUBIF**  : Public interface on the Nova network server.

**CONFIG_NOVA_NETWORK_PRIVIF** : Private interface for Flat DHCP on the Nova network server.

**CONFIG_NOVA_NETWORK_FIXEDRANGE** : IP Range for Flat DHCP ['^([\\d]{1,3}\\.){3}[\\d]{1,3}/\\d\\d?$'].

**CONFIG_NOVA_NETWORK_FLOATRANGE** : IP Range for Floating IP's ['^([\\d]{1,3}\\.){3}[\\d]{1,3}/\\d\\d?$'].

**CONFIG_NOVA_SCHED_HOST**     : The IP address of the server on which to install the Nova Scheduler service.

**CONFIG_NOVA_SCHED_CPU_ALLOC_RATIO** : The overcommitment ratio for virtual to physical CPUs. Set to 1.0 to disable CPU overcommitment.

**CONFIG_NOVA_SCHED_RAM_ALLOC_RATIO** : The overcommitment ratio for virtual to physical RAM. Set to 1.0 to disable RAM overcommitment.

**CONFIG_NOVA_CONDUCTOR_HOST**    : The IP address of the server on which to install the Nova Conductor service.

**CONFIG_NOVA_NETWORK_AUTOASSIGNFLOATINGIP**    : Automatically assign a floating IP to new instances.

**CONFIG_NOVA_NETWORK_DEFAULTFLOATINGPOOL**    : Name of the default floating pool to which the specified floating ranges are added to.

**CONFIG_NOVA_NETWORK_MANAGER**   : Nova network manager.

**CONFIG_NOVA_NETWORK_NUMBER**    : Number of networks to support.

**CONFIG_NOVA_NETWORK_SIZE**      : Number of addresses in each private subnet.

**CONFIG_NOVA_NETWORK_VLAN_START**    : First VLAN for private networks.

NOVACLIENT Config parameters
----------------------------

**CONFIG_OSCLIENT_HOST**       : The IP address of the server on which to install the OpenStack client packages. An admin "rc" file will also be installed.

OpenStack Horizon Config parameters
-----------------------------------

**CONFIG_HORIZON_HOST**        : The IP address of the server on which to install Horizon.

**CONFIG_HORIZON_SSL**         : To set up Horizon communication over https set this to "y" ['y', 'n'].

**CONFIG_SSL_CERT**    : PEM encoded certificate to be used for ssl on the https server, leave blank if one should be generated, this certificate should not require a passphrase.

**CONFIG_SSL_KEY**    : Keyfile corresponding to the certificate if one was entered.

OpenStack Swift Config parameters
---------------------------------

**CONFIG_SWIFT_PROXY_HOSTS**   : The IP address on which to install the Swift proxy service.

**CONFIG_SWIFT_KS_PW**         : The password to use for the Swift to authenticate with Keystone.

**CONFIG_SWIFT_STORAGE_HOSTS** : A comma separated list of IP addresses on which to install the Swift Storage services, each entry should take the format <ipaddress>[/dev], for example 127.0.0.1/vdb will install /dev/vdb on 127.0.0.1 as a swift storage device(packstack does not create the filesystem, you must do this first), if /dev is omitted Packstack will create a loopback device for a test setup.

**CONFIG_SWIFT_STORAGE_ZONES** : Number of swift storage zones, this number MUST be no bigger than the number of storage devices configured.

**CONFIG_SWIFT_STORAGE_REPLICAS** : Number of swift storage replicas, this number MUST be no bigger than the number of storage zones configured.

**CONFIG_SWIFT_STORAGE_FSTYPE** : FileSystem type for storage nodes ['xfs', 'ext4'].

**CONFIG_SWIFT_HASH**    : Shared secret for Swift.

Server Prepare Configs
-----------------------

**CONFIG_USE_EPEL**            : Install OpenStack from EPEL. If set to "y" EPEL will be installed on each server ['y', 'n'].

**CONFIG_REPO**                : A comma separated list of URLs to any additional yum repositories to install.

**CONFIG_RH_USER**             : To subscribe each server with Red Hat subscription manager, include this with CONFIG_RH_PW.

**CONFIG_RH_PW**               : To subscribe each server with Red Hat subscription manager, include this with CONFIG_RH_USER.

**CONFIG_RH_BETA_REPO**        : To subscribe each server with Red Hat subscription manager, to Red Hat Beta RPM's ['y', 'n'].

**CONFIG_SATELLITE_URL**       : To subscribe each server with RHN Satellite,fill Satellite's URL here. Note that either satellite's username/password or activation key has to be provided.

RHN Satellite config
--------------------

**CONFIG_SATELLITE_USER**      : Username to access RHN Satellite.

**CONFIG_SATELLITE_PW**        : Password to access RHN Satellite.

**CONFIG_SATELLITE_AKEY**      : Activation key for subscription to RHN Satellite.

**CONFIG_SATELLITE_CACERT**    : Specify a path or URL to a SSL CA certificate to use.

**CONFIG_SATELLITE_PROFILE**   : If required specify the profile name that should be used as an identifier for the system in RHN Satellite.

**CONFIG_SATELLITE_FLAGS**     : Comma separated list of flags passed to rhnreg_ks. Valid flags are: novirtinfo, norhnsd, nopackages ['novirtinfo', 'norhnsd', 'nopackages'].

**CONFIG_SATELLITE_PROXY**     : Specify a HTTP proxy to use with RHN Satellite.

RHN Satellite proxy config
--------------------------

**CONFIG_SATELLITE_PROXY_USER** : Specify a username to use with an authenticated HTTP proxy.

**CONFIG_SATELLITE_PROXY_PW**  : Specify a password to use with an authenticated HTTP proxy.

Nagios Config parameters
------------------------

**CONFIG_NAGIOS_HOST**         : The IP address of the server on which to install the Nagios server.

**CONFIG_NAGIOS_PW**           : The password of the nagiosadmin user on the Nagios server.

Ceilometer Config Parameters
------------------------

**CONFIG_CEILOMETER_HOST**     : The IP address of the server on which to install Ceilometer.

**CONFIG_CEILOMETER_SECRET**   : Secret key for signing metering messages.

**CONFIG_CEILOMETER_KS_PW**    : The password to use for Ceilometer to authenticate with Keystone.

Heat Config Parameters
------------------------

**CONFIG_HEAT_HOST**               : The IP address of the server on which to install Heat service.

**CONFIG_HEAT_DB_PW**              : The password used by Heat user to authenticate against MySQL.

**CONFIG_HEAT_KS_PW**              : The password to use for the Heat to authenticate with Keystone.

**CONFIG_HEAT_CLOUDWATCH_INSTALL** : Set to 'y' if you would like Packstack to install Heat CloudWatch API.

**CONFIG_HEAT_CFN_INSTALL**        : Set to 'y' if you would like Packstack to install Heat CloudFormation API.

**CONFIG_HEAT_CLOUDWATCH_HOST**    : The IP address of the server on which to install Heat CloudWatch API service.

**CONFIG_HEAT_CFN_HOST**           : The IP address of the server on which to install Heat CloudFormation API.

Neutron Config Parameters.
------------------------

**CONFIG_NEUTRON_SERVER_HOST**            : The IP addresses of the server on which to install the Neutron server.

**CONFIG_NEUTRON_KS_PW**                  : The password to use for Neutron to authenticate with Keystone.

**CONFIG_NEUTRON_DB_PW**                  : The password to use for Neutron to access DB.

**CONFIG_NEUTRON_L3_HOSTS**               : A comma separated list of IP addresses on which to install Neutron L3 agent.

**CONFIG_NEUTRON_L3_EXT_BRIDGE**          : The name of the bridge that the Neutron L3 agent will use for external traffic, or 'provider' if using provider networks.

**CONFIG_NEUTRON_DHCP_HOSTS**             : A comma separated list of IP addresses on which to install Neutron DHCP agent.

**CONFIG_NEUTRON_L2_PLUGIN**              : The name of the L2 plugin to be used with Neutron.

**CONFIG_NEUTRON_METADATA_HOSTS**         : A comma separated list of IP addresses on which to install Neutron metadata agent.

**CONFIG_NEUTRON_METADATA_PW**            : A comma separated list of IP addresses on which to install Neutron metadata agent.

**CONFIG_NEUTRON_LB_TENANT_NETWORK_TYPE** : The type of network to allocate for tenant networks (eg. vlan, local, gre).

**CONFIG_NEUTRON_LB_VLAN_RANGES**         : A comma separated list of VLAN ranges for the Neutron linuxbridge plugin (eg. physnet1:1:4094,physnet2,physnet3:3000:3999).

**CONFIG_NEUTRON_LB_INTERFACE_MAPPINGS**  : A comma separated list of interface mappings for the Neutron linuxbridge plugin (eg. physnet1:br-eth1,physnet2:br-eth2,physnet3:br-eth3).

**CONFIG_NEUTRON_OVS_TENANT_NETWORK_TYPE**          : Type of network to allocate for tenant networks (eg. vlan, local, gre).

**CONFIG_NEUTRON_OVS_VLAN_RANGES**          : A comma separated list of VLAN ranges for the Neutron openvswitch plugin (eg. physnet1:1:4094,physnet2,physnet3:3000:3999).

**CONFIG_NEUTRON_OVS_BRIDGE_MAPPINGS**          : A comma separated list of bridge mappings for the Neutron openvswitch plugin (eg. physnet1:br-eth1,physnet2:br-eth2,physnet3:br-eth3).

**CONFIG_NEUTRON_OVS_BRIDGE_IFACES**          : A comma separated list of colon-separated OVS brid.

**CONFIG_NEUTRON_OVS_TUNNEL_RANGES**          : A comma separated list of tunnel ranges for the Neutron openvswitch plugin.

**CONFIG_NEUTRON_OVS_TUNNEL_IF**          : Override the IP used for GRE tunnels on this hypervisor to the IP found on the specified interface (defaults to the HOST IP).


Provision Config Parameters.
------------------------
**CONFIG_PROVISION_ALL_IN_ONE_OVS_BRIDGE**    : Whether to configure the ovs external bridge in an all-in-one deployment.

**CONFIG_PROVISION_DEMO**    : Whether to provision for demo usage and testing.

**CONFIG_PROVISION_DEMO_FLOATRANGE**    : The CIDR network address for the floating IP subnet.

**CONFIG_PROVISION_TEMPEST**    : Whether to configure tempest for testing.

**CONFIG_PROVISION_TEMPEST_REPO_REVISION**    : The revision of the tempest git repository to use.

**CONFIG_PROVISION_TEMPEST_REPO_URI**    : The uri of the tempest git repository to use.


Log files and Debug info
------------------------

The location of the log files and generated puppet manifests are in the /var/tmp/packstack directory under a directory named by the date in which packstack was run and a random string (e.g. /var/tmp/packstack/20131022-204316-Bf3Ek2). Inside, we find a manifest directory and the openstack-setup.log file; puppet manifests and a log file for each one are found inside the manifest directory.

In case debugging info is needed while running packstack the -d switch will make it write more detailed information about the installation.

Examples:

If we need an allinone debug session:

packstack -d --allinone

If we need a answer file to tailor it and then debug:

packstack --gen-answer-file=ans.txt
packstack -d --answer-file=ans.txt


SOURCE
======
* `packstack      https://github.com/stackforge/packstack`
* `puppet modules https://github.com/puppetlabs and https://github.com/packstack`

