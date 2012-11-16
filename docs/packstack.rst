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
::

  Global Options
    CONFIG_GLANCE_INSTALL : Install Glance? ['y', 'n']
    CONFIG_CINDER_INSTALL : Install Cinder? ['y', 'n']
    CONFIG_NOVA_INSTALL : Install Nova? ['y', 'n']
    CONFIG_DASHBOARD_INSTALL : Install Dashboard? ['y', 'n']
    CONFIG_SWIFT_INSTALL : Install Swift? ['y', 'n']
    CONFIG_CLIENT_INSTALL : Install OS Client server? ['y', 'n']
  SSH Configs 
    CONFIG_SSH_KEY : Public key to install on servers ['/home/derekh/.ssh/id_rsa.pub']
  MySQL Config paramaters
    CONFIG_MYSQL_HOST : Hostname of the MySQL server ''
    CONFIG_MYSQL_USER : Username of the MySQL admin user ''
    CONFIG_MYSQL_PW : Password for the MySQL admin user ''
  QPID Config paramaters
    CONFIG_QPID_HOST : Hostname of the QPID server ''
  Keystone Config paramaters
    CONFIG_KEYSTONE_HOST : Hostname of the Keystone server ''
    CONFIG_KEYSTONE_ADMINTOKEN : Keystone Admin Token ''
    CONFIG_KEYSTONE_ADMINPASSWD : Keystone Admin Password ''
  Glance Config paramaters
    CONFIG_GLANCE_HOST : Hostname of the Glance server ''
  Cinder Config paramaters
    CONFIG_CINDER_HOST : Hostname of the Cinder server ''
  Nova Options
    CONFIG_NOVA_API_HOST : Hostname of the Nova API server ''
    CONFIG_NOVA_CERT_HOST : Hostname of the Nova CERT server ''
    CONFIG_NOVA_COMPUTE_HOSTS : Hostname of the Nova Compute servers (commma seperated) ''
    CONFIG_LIBVIRT_TYPE : Libvirt Type to use ['qemu', 'kvm']
    CONFIG_NOVA_COMPUTE_PRIVIF : Private interface for Flat DHCP on the Nova compute servers ''
    CONFIG_NOVA_NETWORK_HOST : Hostname of the Nova Network server ''
    CONFIG_NOVA_NETWORK_PUBIF : Public interface on the Nova network server ''
    CONFIG_NOVA_NETWORK_PRIVIF : Private interface for Flat DHCP on the Nova network server ''
    CONFIG_NOVA_NETWORK_FIXEDRANGE : Fixed IP Range for Flat DHCP ['^([\\d]{1,3}\\.){3}[\\d]{1,3}/\\d\\d?$']
    CONFIG_NOVA_NETWORK_FLOATINGRANGE : Fixed IP Range for Floating IP's ['^([\\d]{1,3}\\.){3}[\\d]{1,3}/\\d\\d?$']
    CONFIG_NOVA_SCHED_HOST : Hostname of the Nova Sched server ''
  NOVACLIENT Config paramaters
    CONFIG_OSCLIENT_HOST : Hostname of the OpenStack client ''
  OpenStack Dashboard Config paramaters
    CONFIG_DASHBOARD_HOST : Hostname of the Dashoard ''
    CONFIG_DASHBOARD_SECRET_KEY : Keystone Secret Encryption Key ''
  OpenStack Swift Config paramaters
    CONFIG_SWIFT_PROXY_HOSTS : Hostname of the Swift Proxy server ''
    CONFIG_SWIFT_STORAGE_HOSTS : Hostname of the Swift Storage servers e.g. host/dev,host/dev ''
    CONFIG_SWIFT_STORAGE_ZONES : Number of swift storage zone ''
    CONFIG_SWIFT_STORAGE_REPLICAS : Number of swift storage replicas ''
    CONFIG_SWIFT_STORAGE_FSTYPE : FileSystem type for storage nodes ['xfs', 'ext4']
  Server Prepare Configs 
    CONFIG_USE_EPEL : Install openstack from epel ['y', 'n']
  Puppet Config paramaters
    CONFIG_PUPPET_REMOVEMODULES : Causes the Puppet modules to be removed (if present), and as a result re-cloned from git ['y', 'n']


SOURCE
======
* `packstack      https://github.com/fedora-openstack/packstack`
* `installer      https://github.com/derekhiggins/installer`
* `puppet modules https://github.com/puppetlabs`
