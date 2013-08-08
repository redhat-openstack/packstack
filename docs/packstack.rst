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

**CONFIG_GLANCE_INSTALL**      : Set to 'y' if you would like Packstack to install Glance ['y', 'n']

**CONFIG_CINDER_INSTALL**      : Set to 'y' if you would like Packstack to install Cinder ['y', 'n']

**CONFIG_NOVA_INSTALL**        : Set to 'y' if you would like Packstack to install Nova ['y', 'n']

**CONFIG_HORIZON_INSTALL**     : Set to 'y' if you would like Packstack to install Horizon ['y', 'n']

**CONFIG_SWIFT_INSTALL**       : Set to 'y' if you would like Packstack to install Swift ['y', 'n']

**CONFIG_CLIENT_INSTALL**      : Set to 'y' if you would like Packstack to install the OpenStack Client packages. An admin "rc" file will also be installed ['y', 'n']

**CONFIG_NTP_SERVERS**         : Comma separated list of NTP servers. Leave plain if Packstack should not install ntpd on instances.

**CONFIG_NAGIOS_INSTALL**      : Set to 'y' if you would like Packstack to install Nagios to monitor openstack hosts ['y', 'n']

SSH Configs
------------

**CONFIG_SSH_KEY**             : Path to a Public key to install on servers. If a usable key has not been installed on the remote servers the user will be prompted for a password and this key will be installed so the password will not be required again

MySQL Config parameters
-----------------------

**CONFIG_MYSQL_HOST**          : The IP address of the server on which to install MySQL

**CONFIG_MYSQL_USER**          : Username for the MySQL admin user

**CONFIG_MYSQL_PW**            : Password for the MySQL admin user

QPID Config parameters
----------------------

**CONFIG_QPID_HOST**           : The IP address of the server on which to install the QPID service

Keystone Config parameters
--------------------------

**CONFIG_KEYSTONE_HOST**       : The IP address of the server on which to install Keystone

**CONFIG_KEYSTONE_DB_PW**      : The password to use for the Keystone to access DB

**CONFIG_KEYSTONE_ADMIN_TOKEN** : The token to use for the Keystone service api

**CONFIG_KEYSTONE_ADMIN_PW**   : The password to use for the Keystone admin user

Glance Config parameters
------------------------

**CONFIG_GLANCE_HOST**         : The IP address of the server on which to install Glance

**CONFIG_GLANCE_DB_PW**        : The password to use for the Glance to access DB

**CONFIG_GLANCE_KS_PW**        : The password to use for the Glance to authenticate with Keystone

Cinder Config parameters
------------------------

**CONFIG_CINDER_HOST**         : The IP address of the server on which to install Cinder

**CONFIG_CINDER_DB_PW**        : The password to use for the Cinder to access DB

**CONFIG_CINDER_KS_PW**        : The password to use for the Cinder to authenticate with Keystone

**CONFIG_CINDER_BACKEND**      : The Cinder backend to use ['lvm', 'gluster', 'nfs']

Cinder volume create Config parameters
--------------------------------------

**CONFIG_CINDER_VOLUMES_CREATE** : Create Cinder's volumes group ['y', 'n']

Cinder volume size Config parameters
------------------------------------

**CONFIG_CINDER_VOLUMES_SIZE** : Cinder's volumes group size

Cinder gluster Config parameters
--------------------------------

**CONFIG_CINDER_GLUSTER_MOUNTS** : A single or comma separated list of gluster volume shares

Cinder NFS Config parameters
----------------------------

**CONFIG_CINDER_NFS_MOUNTS**   : A single or comma seprated list of NFS exports to mount

Nova Options
------------

**CONFIG_NOVA_API_HOST**       : The IP address of the server on which to install the Nova API service

**CONFIG_NOVA_CERT_HOST**      : The IP address of the server on which to install the Nova Cert service

**CONFIG_NOVA_VNCPROXY_HOST**  : The IP address of the server on which to install the Nova VNC proxy

**CONFIG_NOVA_COMPUTE_HOSTS**  : A comma separated list of IP addresses on which to install the Nova Compute services

**CONFIG_NOVA_COMPUTE_PRIVIF** : Private interface for Flat DHCP on the Nova compute servers

**CONFIG_NOVA_NETWORK_HOST**   : The IP address of the server on which to install the Nova Network service

**CONFIG_NOVA_DB_PW**          : The password to use for the Nova to access DB

**CONFIG_NOVA_KS_PW**          : The password to use for the Nova to authenticate with Keystone

**CONFIG_NOVA_NETWORK_PUBIF**  : Public interface on the Nova network server

**CONFIG_NOVA_NETWORK_PRIVIF** : Private interface for Flat DHCP on the Nova network server

**CONFIG_NOVA_NETWORK_FIXEDRANGE** : IP Range for Flat DHCP ['^([\\d]{1,3}\\.){3}[\\d]{1,3}/\\d\\d?$']

**CONFIG_NOVA_NETWORK_FLOATRANGE** : IP Range for Floating IP's ['^([\\d]{1,3}\\.){3}[\\d]{1,3}/\\d\\d?$']

**CONFIG_NOVA_SCHED_HOST**     : The IP address of the server on which to install the Nova Scheduler service

**CONFIG_NOVA_SCHED_CPU_ALLOC_RATIO** : The overcommitment ratio for virtual to physical CPUs. Set to 1.0 to disable CPU overcommitment

**CONFIG_NOVA_SCHED_RAM_ALLOC_RATIO** : The overcommitment ratio for virtual to physical RAM. Set to 1.0 to disable RAM overcommitment

NOVACLIENT Config parameters
----------------------------

**CONFIG_OSCLIENT_HOST**       : The IP address of the server on which to install the OpenStack client packages. An admin "rc" file will also be installed

OpenStack Horizon Config parameters
-----------------------------------

**CONFIG_HORIZON_HOST**        : The IP address of the server on which to install Horizon

**CONFIG_HORIZON_SSL**         : To set up Horizon communication over https set this to "y" ['y', 'n']

OpenStack Swift Config parameters
---------------------------------

**CONFIG_SWIFT_PROXY_HOSTS**   : The IP address on which to install the Swift proxy service

**CONFIG_SWIFT_KS_PW**         : The password to use for the Swift to authenticate with Keystone

**CONFIG_SWIFT_STORAGE_HOSTS** : A comma separated list of IP addresses on which to install the Swift Storage services, each entry should take the format <ipaddress>[/dev], for example 127.0.0.1/vdb will install /dev/vdb on 127.0.0.1 as a swift storage device(packstack does not create the filesystem, you must do this first), if /dev is omitted Packstack will create a loopback device for a test setup

**CONFIG_SWIFT_STORAGE_ZONES** : Number of swift storage zones, this number MUST be no bigger than the number of storage devices configured

**CONFIG_SWIFT_STORAGE_REPLICAS** : Number of swift storage replicas, this number MUST be no bigger than the number of storage zones configured

**CONFIG_SWIFT_STORAGE_FSTYPE** : FileSystem type for storage nodes ['xfs', 'ext4']

Server Prepare Configs
-----------------------

**CONFIG_USE_EPEL**            : Install OpenStack from EPEL. If set to "y" EPEL will be installed on each server ['y', 'n']

**CONFIG_REPO**                : A comma separated list of URLs to any additional yum repositories to install

**CONFIG_RH_USER**             : To subscribe each server with Red Hat subscription manager, include this with CONFIG_RH_PW

**CONFIG_RH_PW**               : To subscribe each server with Red Hat subscription manager, include this with CONFIG_RH_USER

**CONFIG_RH_BETA_REPO**        : To subscribe each server with Red Hat subscription manager, to Red Hat Beta RPM's ['y', 'n']

**CONFIG_SATELLITE_URL**       : To subscribe each server with RHN Satellite,fill Satellite's URL here. Note that either satellite's username/password or activation key has to be provided

RHN Satellite config
--------------------

**CONFIG_SATELLITE_USER**      : Username to access RHN Satellite

**CONFIG_SATELLITE_PW**        : Password to access RHN Satellite

**CONFIG_SATELLITE_AKEY**      : Activation key for subscription to RHN Satellite

**CONFIG_SATELLITE_CACERT**    : Specify a path or URL to a SSL CA certificate to use

**CONFIG_SATELLITE_PROFILE**   : If required specify the profile name that should be used as an identifier for the system in RHN Satellite

**CONFIG_SATELLITE_FLAGS**     : Comma separated list of flags passed to rhnreg_ks. Valid flags are: novirtinfo, norhnsd, nopackages ['novirtinfo', 'norhnsd', 'nopackages']

**CONFIG_SATELLITE_PROXY**     : Specify a HTTP proxy to use with RHN Satellite

RHN Satellite proxy config
--------------------------

**CONFIG_SATELLITE_PROXY_USER** : Specify a username to use with an authenticated HTTP proxy

**CONFIG_SATELLITE_PROXY_PW**  : Specify a password to use with an authenticated HTTP proxy.

Nagios Config parameters
------------------------

**CONFIG_NAGIOS_HOST**         : The IP address of the server on which to install the Nagios server

**CONFIG_NAGIOS_PW**           : The password of the nagiosadmin user on the Nagios server


SOURCE
======
* `packstack      https://github.com/stackforge/packstack`
* `puppet modules https://github.com/puppetlabs and https://github.com/packstack`
