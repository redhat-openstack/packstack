==============
packstack
==============

SYNOPSIS
========

  packstack [options]

DESCRIPTION
===========
  Packstack is a utility that uses uses puppet modules to install openstack. It can be used to install each openstack service on seperate servers, all on one server or any combination of these. There are 3 ways that packstack can be run.
- packstack
- packstack [options]
- packstack --gen-answer-file=<file>  / packstack --answer-file=<file>

  The third of these options allows the user to generate a default answer file, edit the default options and finally run packstack a second time using this answerfile, this is the easyies way to run packstack and the one that will be documented here. When <file> is created the OPTIONS below will be contained and can be edited by the user.

OPTIONS
=======

Global Options
--------------

**CONFIG_GLANCE_INSTALL**      : Selects if packstack does or does not install Glance ['y', 'n']

**CONFIG_CINDER_INSTALL**      : Selects if packstack does or does not install Cinder ['y', 'n']

**CONFIG_NOVA_INSTALL**        : Selects if packstack does or does not install Nova ['y', 'n']

**CONFIG_HORIZON_INSTALL**     : Selects if packstack does or does not install Horizon ['y', 'n']

**CONFIG_SWIFT_INSTALL**       : Selects if packstack does or does not install swift ['y', 'n']

**CONFIG_CLIENT_INSTALL**      : Selects if packstack does or does not install the openstack client packages, a admin "rc" file will also be installed ['y', 'n']

SSH Configs
------------

**CONFIG_SSH_KEY**             : Public key to install on servers, if a usable key has not been installed on remote servers the user will be prompted for a password and this key will be installed so the password will not be required again ['/home/derekh/.ssh/id_rsa.pub']

MySQL Config paramaters
-----------------------

**CONFIG_MYSQL_HOST**          : The IP address of the server on which to install MySQL

**CONFIG_MYSQL_USER**          : Username of the MySQL admin user

**CONFIG_MYSQL_PW**            : Password for the MySQL admin user

QPID Config paramaters
----------------------

**CONFIG_QPID_HOST**           : The IP address of the server on which to install the QPID service

Keystone Config paramaters
--------------------------

**CONFIG_KEYSTONE_HOST**       : The IP address of the server on which to install Keystone

**CONFIG_KEYSTONE_ADMINTOKEN** : The token to use for the keystone service api

**CONFIG_KEYSTONE_ADMINPASSWD** : The token password to use for the keystone admin user

Glance Config paramaters
------------------------

**CONFIG_GLANCE_HOST**         : The IP address of the server on which to install Glance

Cinder Config paramaters
------------------------

**CONFIG_CINDER_HOST**         : The IP address of the server on which to install Cinder

Nova Options
------------

**CONFIG_NOVA_API_HOST**       : The IP address of the server on which to install the Nova API service

**CONFIG_NOVA_CERT_HOST**      : The IP address of the server on which to install the Nova Cert service

**CONFIG_NOVA_COMPUTE_HOSTS**  : A comma seperated list of IP addresses on which to install the Nova Compute services

**CONFIG_LIBVIRT_TYPE**        : The libvirt type to use, if your compute server is bare metal set to kvm, if testing on a vm set to qemu ['qemu', 'kvm']

**CONFIG_NOVA_COMPUTE_PRIVIF** : Private interface for Flat DHCP on the Nova compute servers

**CONFIG_NOVA_NETWORK_HOST**   : The IP address of the server on which to install the Nova Network service

**CONFIG_NOVA_NETWORK_PUBIF**  : Public interface on the Nova network server

**CONFIG_NOVA_NETWORK_PRIVIF** : Private interface for Flat DHCP on the Nova network server

**CONFIG_NOVA_NETWORK_FIXEDRANGE** : IP Range for Flat DHCP ['^([\\d]{1,3}\\.){3}[\\d]{1,3}/\\d\\d?$']

**CONFIG_NOVA_NETWORK_FLOATRANGE** : IP Range for Floating IP's ['^([\\d]{1,3}\\.){3}[\\d]{1,3}/\\d\\d?$']

**CONFIG_NOVA_SCHED_HOST**     : The IP address of the server on which to install the Nova Scheduler service

NOVACLIENT Config paramaters
----------------------------

**CONFIG_OSCLIENT_HOST**       : The IP address of the server on which to install the openstack client packages, an admin "rc" file will also be installed

OpenStack Horizon Config paramaters
-----------------------------------

**CONFIG_HORIZON_HOST**        : The IP address of the server on which to install Horizon

**CONFIG_HORIZON_SECRET_KEY**  : Keystone Secret Encryption Key

OpenStack Swift Config paramaters
---------------------------------

**CONFIG_SWIFT_PROXY_HOSTS**   : A comma seperated list of IP addresses on which to install the Swift proxy services

**CONFIG_SWIFT_STORAGE_HOSTS** : A comma seperated list of IP addresses on which to install the Swift Storage services, each entry should take the format <ipaddress>[/dev], for example 127.0.0.1/vdb will install /dev/vdb on 127.0.0.1 as a swift storage device, if /dev is ommited packstack will create a loopback device for a test setup

**CONFIG_SWIFT_STORAGE_ZONES** : Number of swift storage zones, this number MUST be no bigger then number of storage devices configered

**CONFIG_SWIFT_STORAGE_REPLICAS** : Number of swift storage replicas, this number MUST be no bigger then number of storage zones configered

**CONFIG_SWIFT_STORAGE_FSTYPE** : FileSystem type for storage nodes ['xfs', 'ext4']

Server Prepare Configs
-----------------------

**CONFIG_USE_EPEL**            : Install openstack from epel, If set to "n" this causes EPEL to be permanently disabled before installing openstack, i.e. you should have alternative openstack repositories in place ['y', 'n']


SOURCE
======
* `packstack      https://github.com/fedora-openstack/packstack`
* `installer      https://github.com/derekhiggins/installer`
* `puppet modules https://github.com/puppetlabs`
