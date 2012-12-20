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

Installer Config parameters
---------------------------

**CONFIG_DEBUG**               : Should we turn on debug in logging ['y', 'n']

SSH Configs
------------

**CONFIG_SSH_KEY**             : Path to a Public key to install on servers. If a usable key has not been installed on the remote servers the user will be prompted for a password and this key will be installed so the password will not be required again

Global Options
--------------

**CONFIG_GLANCE_INSTALL**      : Set to 'y' if you would like Packstack to install Glance ['y', 'n']

**CONFIG_CINDER_INSTALL**      : Set to 'y' if you would like Packstack to install Cinder ['y', 'n']

**CONFIG_NOVA_INSTALL**        : Set to 'y' if you would like Packstack to install Nova ['y', 'n']

**CONFIG_HORIZON_INSTALL**     : Set to 'y' if you would like Packstack to install Horizon ['y', 'n']

**CONFIG_SWIFT_INSTALL**       : Set to 'y' if you would like Packstack to install Swift ['y', 'n']

**CONFIG_CLIENT_INSTALL**      : Set to 'y' if you would like Packstack to install the openstack client packages. An admin "rc" file will also be installed ['y', 'n']

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

**CONFIG_KEYSTONE_ADMINTOKEN** : The token to use for the Keystone service api

**CONFIG_KEYSTONE_ADMINPASSWD** : The password to use for the Keystone admin user

Glance Config parameters
------------------------

**CONFIG_GLANCE_HOST**         : The IP address of the server on which to install Glance

Cinder Config parameters
------------------------

**CONFIG_CINDER_HOST**         : The IP address of the server on which to install Cinder

Nova Options
------------

**CONFIG_NOVA_API_HOST**       : The IP address of the server on which to install the Nova API service

**CONFIG_NOVA_CERT_HOST**      : The IP address of the server on which to install the Nova Cert service

**CONFIG_NOVA_VNCPROXY_HOST**  : The IP address of the server on which to install the Nova VNC proxy

**CONFIG_NOVA_COMPUTE_HOSTS**  : A comma separated list of IP addresses on which to install the Nova Compute services

**CONFIG_NOVA_COMPUTE_PRIVIF** : Private interface for Flat DHCP on the Nova compute servers

**CONFIG_NOVA_NETWORK_HOST**   : The IP address of the server on which to install the Nova Network service

**CONFIG_NOVA_NETWORK_PUBIF**  : Public interface on the Nova network server

**CONFIG_NOVA_NETWORK_PRIVIF** : Private interface for Flat DHCP on the Nova network server

**CONFIG_NOVA_NETWORK_FIXEDRANGE** : IP Range for Flat DHCP ['^([\\d]{1,3}\\.){3}[\\d]{1,3}/\\d\\d?$']

**CONFIG_NOVA_NETWORK_FLOATRANGE** : IP Range for Floating IP's ['^([\\d]{1,3}\\.){3}[\\d]{1,3}/\\d\\d?$']

**CONFIG_NOVA_SCHED_HOST**     : The IP address of the server on which to install the Nova Scheduler service

NOVACLIENT Config parameters
----------------------------

**CONFIG_OSCLIENT_HOST**       : The IP address of the server on which to install the openstack client packages. An admin "rc" file will also be installed

OpenStack Horizon Config parameters
-----------------------------------

**CONFIG_HORIZON_HOST**        : The IP address of the server on which to install Horizon

**CONFIG_HORIZON_SECRET_KEY**  : Horizon Secret Encryption Key

OpenStack Swift Config parameters
---------------------------------

**CONFIG_SWIFT_PROXY_HOSTS**   : The IP address on which to install the Swift proxy service

**CONFIG_SWIFT_STORAGE_HOSTS** : A comma separated list of IP addresses on which to install the Swift Storage services, each entry should take the format <ipaddress>[/dev], for example 127.0.0.1/vdb will install /dev/vdb on 127.0.0.1 as a swift storage device, if /dev is omitted Packstack will create a loopback device for a test setup

**CONFIG_SWIFT_STORAGE_ZONES** : Number of swift storage zones, this number MUST be no bigger than the number of storage devices configured

**CONFIG_SWIFT_STORAGE_REPLICAS** : Number of swift storage replicas, this number MUST be no bigger than the number of storage zones configured

**CONFIG_SWIFT_STORAGE_FSTYPE** : FileSystem type for storage nodes ['xfs', 'ext4']

Server Prepare Configs
-----------------------

**CONFIG_USE_EPEL**            : Install OpenStack from EPEL. If set to "y" EPEL will be installed on each server ['y', 'n']

**CONFIG_REPO**                : A comma separated list of URLs to any additional yum repositories to install

**CONFIG_RH_USERNAME**         : To subscribe each server with Red Hat subscription manager, include this with CONFIG_RH_PASSWORD

**CONFIG_RH_PASSWORD**         : To subscribe each server with Red Hat subscription manager, include this with CONFIG_RH_USERNAME


SOURCE
======
* `packstack      https://github.com/fedora-openstack/packstack`
* `installer      https://github.com/derekhiggins/installer`
* `puppet modules https://github.com/puppetlabs`
