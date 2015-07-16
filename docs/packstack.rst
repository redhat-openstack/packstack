=========
Packstack
=========

SYNOPSIS
========

packstack [options]

DESCRIPTION
===========

Packstack is a utility that uses uses puppet modules to install OpenStack. It can be used to install each openstack service on separate servers, all on one server or any combination of these. There are 3 ways that Packstack can be run.

- packstack
- packstack [options]
- packstack --gen-answer-file=<file> [options] / packstack --answer-file=<file>

The third option allows the user to generate a default answer file, edit the default options and finally run Packstack a second time using this answer file. This is the easiest way to run Packstack and the one that will be documented here. Optionally, it is possible to set additional command-line options (such as a default password), and those options will be set in the answer file.

When <file> is created, it will contain the OPTIONS below, which can then be edited by the user.

OPTIONS
=======

Global Options
--------------

**CONFIG_SSH_KEY**
    Path to a Public key to install on servers. If a usable key has not been installed on the remote servers the user will be prompted for a password and this key will be installed so the password will not be required again

**CONFIG_DEFAULT_PASSWORD**
    Set a default password everywhere. The default password will be overriden by whatever password is set for each individual service or user.

**CONFIG_MARIADB_INSTALL**
    Set to 'y' if you would like Packstack to install MariaDB ['y', 'n']

**CONFIG_GLANCE_INSTALL**
    Set to 'y' if you would like Packstack to install OpenStack Image Service (Glance) ['y', 'n']

**CONFIG_CINDER_INSTALL**
    Set to 'y' if you would like Packstack to install OpenStack Block Storage (Cinder) ['y', 'n']

**CONFIG_NOVA_INSTALL**
    Set to 'y' if you would like Packstack to install OpenStack Compute (Nova) ['y', 'n']

**CONFIG_NEUTRON_INSTALL**
    Set to 'y' if you would like Packstack to install OpenStack Networking (Neutron). Otherwise Nova Network will be used. ['y', 'n']

**CONFIG_HORIZON_INSTALL**
    Set to 'y' if you would like Packstack to install OpenStack Dashboard (Horizon) ['y', 'n']

**CONFIG_SWIFT_INSTALL**
    Set to 'y' if you would like Packstack to install OpenStack Object Storage (Swift) ['y', 'n']

**CONFIG_CEILOMETER_INSTALL**
    Set to 'y' if you would like Packstack to install OpenStack Metering (Ceilometer) ['y', 'n']

**CONFIG_HEAT_INSTALL**
    Set to 'y' if you would like Packstack to install OpenStack Orchestration (Heat) ['y', 'n']

**CONFIG_SAHARA_INSTALL**
    Set to 'y' if you would like Packstack to install OpenStack Clustering (Sahara) ['y', 'n']

**CONFIG_TROVE_INSTALL**
    Set to 'y' if you would like Packstack to install OpenStack Database (Trove) ['y', 'n']

**CONFIG_IRONIC_INSTALL**
    Set to 'y' if you would like Packstack to install OpenStack Bare Metal (Ironic) ['y', 'n']

**CONFIG_CLIENT_INSTALL**
    Set to 'y' if you would like Packstack to install the OpenStack Client packages. An admin "rc" file will also be installed ['y', 'n']

**CONFIG_NTP_SERVERS**
    Comma separated list of NTP servers. Leave plain if Packstack should not install ntpd on instances.

**CONFIG_NAGIOS_INSTALL**
    Set to 'y' if you would like Packstack to install Nagios to monitor OpenStack hosts ['y', 'n']

**EXCLUDE_SERVERS**
    Comma separated list of servers to be excluded from installation in case you are running Packstack the second time with the same answer file and don't want Packstack to touch these servers. Leave plain if you don't need to exclude any server.

**CONFIG_DEBUG_MODE**
    Set to 'y' if you want to run OpenStack services in debug mode. Otherwise set to 'n'. ['y', 'n']

**CONFIG_CONTROLLER_HOST**
    The IP address of the server on which to install OpenStack services specific to controller role such as API servers, Horizon, etc.

**CONFIG_COMPUTE_HOSTS**
    The list of IP addresses of the server on which to install the Nova compute service

**CONFIG_NETWORK_HOSTS**
    The list of IP addresses of the server on which to install the network service such as Nova network or Neutron

**CONFIG_VMWARE_BACKEND**
    Set to 'y' if you want to use VMware vCenter as hypervisor and storage. Otherwise set to 'n'. ['y', 'n']

**CONFIG_UNSUPPORTED**
    Set to 'y' if you want to use unsupported parameters. This should be used only if you know what you are doing.Issues caused by using unsupported options won't be fixed before next major release. ['y', 'n']

vCenter Config Parameters
-------------------------

**CONFIG_VCENTER_HOST**
    The IP address of the VMware vCenter server

**CONFIG_VCENTER_USER**
    The username to authenticate to VMware vCenter server

**CONFIG_VCENTER_PASSWORD**
    The password to authenticate to VMware vCenter server

**CONFIG_VCENTER_CLUSTER_NAME**
    The name of the vCenter cluster

Global unsupported options
--------------------------

**CONFIG_STORAGE_HOST**
    (Unsupported!) The IP address of the server on which to install OpenStack services specific to storage servers such as Glance and Cinder.

**CONFIG_SAHARA_HOST**
    (Unsupported!) The IP address of the server on which to install OpenStack services specific to Sahara

Server Prepare Configs
-----------------------

**CONFIG_USE_EPEL**
    To subscribe each server to EPEL enter "y" ['y', 'n']

**CONFIG_REPO**
    A comma separated list of URLs to any additional yum repositories to install

RHEL config
-----------

**CONFIG_RH_USER**
    To subscribe each server with Red Hat subscription manager, include this with CONFIG_RH_PW

**CONFIG_SATELLITE_URL**
    To subscribe each server with RHN Satellite,fill Satellite's URL here. Note that either satellite's username/password or activation key has to be provided

RH subscription manager config
------------------------------

**CONFIG_RH_PW**
    To subscribe each server with Red Hat subscription manager, include this with CONFIG_RH_USER

**CONFIG_RH_OPTIONAL**
    To enable RHEL optional repos use value "y" ['y', 'n']

**CONFIG_RH_PROXY**
    Specify a HTTP proxy to use with Red Hat subscription manager

RH subscription manager proxy config
------------------------------------

**CONFIG_RH_PROXY_PORT**
    Specify port of Red Hat subscription manager HTTP proxy

**CONFIG_RH_PROXY_USER**
    Specify a username to use with Red Hat subscription manager HTTP proxy

**CONFIG_RH_PROXY_PW**
    Specify a password to use with Red Hat subscription manager HTTP proxy

RHN Satellite config
--------------------

**CONFIG_SATELLITE_USER**
    Username to access RHN Satellite

**CONFIG_SATELLITE_PW**
    Password to access RHN Satellite

**CONFIG_SATELLITE_AKEY**
    Activation key for subscription to RHN Satellite

**CONFIG_SATELLITE_CACERT**
    Specify a path or URL to a SSL CA certificate to use

**CONFIG_SATELLITE_PROFILE**
    If required specify the profile name that should be used as an identifier for the system in RHN Satellite

**CONFIG_SATELLITE_FLAGS**
    Comma separated list of flags passed to rhnreg_ks. Valid flags are: novirtinfo, norhnsd, nopackages ['novirtinfo', 'norhnsd', 'nopackages']

**CONFIG_SATELLITE_PROXY**
    Specify a HTTP proxy to use with RHN Satellite

RHN Satellite proxy config
--------------------------

**CONFIG_SATELLITE_PROXY_USER**
    Specify a username to use with an authenticated HTTP proxy

**CONFIG_SATELLITE_PROXY_PW**
    Specify a password to use with an authenticated HTTP proxy.

AMQP Config parameters
----------------------

**CONFIG_AMQP_BACKEND**
    Set the AMQP service backend. Allowed values are: qpid, rabbitmq ['qpid', 'rabbitmq']

**CONFIG_AMQP_HOST**
    The IP address of the server on which to install the AMQP service

**CONFIG_AMQP_ENABLE_SSL**
    Enable SSL for the AMQP service ['y', 'n']

**CONFIG_AMQP_ENABLE_AUTH**
    Enable Authentication for the AMQP service ['y', 'n']

AMQP Config SSL parameters
--------------------------

**CONFIG_AMQP_NSS_CERTDB_PW**
    The password for the NSS certificate database of the AMQP service

**CONFIG_AMQP_SSL_PORT**
    The port in which the AMQP service listens to SSL connections

**CONFIG_AMQP_SSL_CACERT_FILE**
    The filename of the CAcertificate that the AMQP service is going to use for verification

**CONFIG_AMQP_SSL_CERT_FILE**
    The filename of the certificate that the AMQP service is going to use

**CONFIG_AMQP_SSL_KEY_FILE**
    The filename of the private key that the AMQP service is going to use

**CONFIG_AMQP_SSL_SELF_SIGNED**
    Auto Generates self signed SSL certificate and key ['y', 'n']

AMQP Config Athentication parameters
------------------------------------

**CONFIG_AMQP_AUTH_USER**
    User for amqp authentication

**CONFIG_AMQP_AUTH_PASSWORD**
    Password for user authentication ['y', 'n']

MariaDB Config parameters
-------------------------

**CONFIG_MARIADB_HOST**
    The IP address of the server on which to install MariaDB or IP address of DB server to use if MariaDB installation was not selected

**CONFIG_MARIADB_USER**
    Username for the MariaDB admin user

**CONFIG_MARIADB_PW**
    Password for the MariaDB admin user

Keystone Config parameters
--------------------------

**CONFIG_KEYSTONE_DB_PW**
    The password to use for the Keystone to access DB

**CONFIG_KEYSTONE_REGION**
    Region name

**CONFIG_KEYSTONE_ADMIN_TOKEN**
    The token to use for the Keystone service api

**CONFIG_KEYSTONE_ADMIN_USERNAME**
    User name for the Identity service 'admin' user.  Defaults to 'admin'.

**CONFIG_KEYSTONE_ADMIN_PW**
    The password to use for the Keystone admin user

**CONFIG_KEYSTONE_ADMIN_EMAIL**
    Email address for the Identity service 'admin' user.  Defaults to 'root@localhost'.

**CONFIG_KEYSTONE_DEMO_PW**
    The password to use for the Keystone demo user

**CONFIG_KEYSTONE_API_VERSION**
    Keystone API version string ['v2.0', 'v3']

**CONFIG_KEYSTONE_TOKEN_FORMAT**
    Keystone token format. Use either UUID or PKI ['UUID', 'PKI']

**CONFIG_KEYSTONE_SERVICE_NAME**
    Name of service to use to run keystone (keystone or httpd) ['keystone', 'httpd']

**CONFIG_KEYSTONE_IDENTITY_BACKEND**
    Type of identity backend (sql or ldap) ['sql', 'ldap']

Keystone LDAP Identity Backend Config parameters
------------------------------------------------

**CONFIG_KEYSTONE_LDAP_URL**
    Keystone LDAP backend URL

**CONFIG_KEYSTONE_LDAP_USER_DN**
    Keystone LDAP backend user DN.  Used to bind to the LDAP server when the LDAP server does not allow anonymous authentication.

**CONFIG_KEYSTONE_LDAP_USER_PASSWORD**
    Keystone LDAP backend password for user DN

**CONFIG_KEYSTONE_LDAP_SUFFIX**
    Keystone LDAP backend base suffix

**CONFIG_KEYSTONE_LDAP_QUERY_SCOPE**
    Keystone LDAP backend query scope (base, one, sub) ['base', 'one', 'sub']

**CONFIG_KEYSTONE_LDAP_PAGE_SIZE**
    Keystone LDAP backend query page size

**CONFIG_KEYSTONE_LDAP_USER_SUBTREE**
    Keystone LDAP backend user subtree

**CONFIG_KEYSTONE_LDAP_USER_FILTER**
    Keystone LDAP backend user query filter

**CONFIG_KEYSTONE_LDAP_USER_OBJECTCLASS**
    Keystone LDAP backend user objectclass

**CONFIG_KEYSTONE_LDAP_USER_ID_ATTRIBUTE**
    Keystone LDAP backend user ID attribute

**CONFIG_KEYSTONE_LDAP_USER_NAME_ATTRIBUTE**
    Keystone LDAP backend user name attribute

**CONFIG_KEYSTONE_LDAP_USER_MAIL_ATTRIBUTE**
    Keystone LDAP backend user email address attribute

**CONFIG_KEYSTONE_LDAP_USER_ENABLED_ATTRIBUTE**
    Keystone LDAP backend user enabled attribute

**CONFIG_KEYSTONE_LDAP_USER_ENABLED_MASK**
    Keystone LDAP backend - bit mask applied to user enabled attribute

**CONFIG_KEYSTONE_LDAP_USER_ENABLED_DEFAULT**
    Keystone LDAP backend - value of enabled attribute which indicates user is enabled

**CONFIG_KEYSTONE_LDAP_USER_ENABLED_INVERT**
    Keystone LDAP backend - users are disabled not enabled ['n', 'y']

**CONFIG_KEYSTONE_LDAP_USER_ATTRIBUTE_IGNORE**
    Comma separated list of attributes stripped from user entry upon update

**CONFIG_KEYSTONE_LDAP_USER_DEFAULT_PROJECT_ID_ATTRIBUTE**
    Keystone LDAP attribute mapped to default_project_id for users

**CONFIG_KEYSTONE_LDAP_USER_ALLOW_CREATE**
    Set to 'y' if you want to be able to create Keystone users through the Keystone interface.  Set to 'n' if you will create directly in the LDAP backend. ['n', 'y']

**CONFIG_KEYSTONE_LDAP_USER_ALLOW_UPDATE**
    Set to 'y' if you want to be able to update Keystone users through the Keystone interface.  Set to 'n' if you will update directly in the LDAP backend. ['n', 'y']

**CONFIG_KEYSTONE_LDAP_USER_ALLOW_DELETE**
    Set to 'y' if you want to be able to delete Keystone users through the Keystone interface.  Set to 'n' if you will delete directly in the LDAP backend. ['n', 'y']

**CONFIG_KEYSTONE_LDAP_USER_PASS_ATTRIBUTE**
    Keystone LDAP attribute mapped to password

**CONFIG_KEYSTONE_LDAP_USER_ENABLED_EMULATION_DN**
    DN of the group entry to hold enabled users when using enabled emulation.

**CONFIG_KEYSTONE_LDAP_USER_ADDITIONAL_ATTRIBUTE_MAPPING**
    List of additional LDAP attributes used for mapping additional attribute mappings for users. Attribute mapping format is <ldap_attr>:<user_attr>, where ldap_attr is the attribute in the LDAP entry and user_attr is the Identity API attribute.

**CONFIG_KEYSTONE_LDAP_GROUP_SUBTREE**
    Keystone LDAP backend group subtree

**CONFIG_KEYSTONE_LDAP_GROUP_FILTER**
    Keystone LDAP backend group query filter

**CONFIG_KEYSTONE_LDAP_GROUP_OBJECTCLASS**
    Keystone LDAP backend group objectclass

**CONFIG_KEYSTONE_LDAP_GROUP_ID_ATTRIBUTE**
    Keystone LDAP backend group ID attribute

**CONFIG_KEYSTONE_LDAP_GROUP_NAME_ATTRIBUTE**
    Keystone LDAP backend group name attribute

**CONFIG_KEYSTONE_LDAP_GROUP_MEMBER_ATTRIBUTE**
    Keystone LDAP backend group member attribute

**CONFIG_KEYSTONE_LDAP_GROUP_DESC_ATTRIBUTE**
    Keystone LDAP backend group description attribute

**CONFIG_KEYSTONE_LDAP_GROUP_ATTRIBUTE_IGNORE**
    Comma separated list of attributes stripped from group entry upon update

**CONFIG_KEYSTONE_LDAP_GROUP_ALLOW_CREATE**
    Set to 'y' if you want to be able to create Keystone groups through the Keystone interface.  Set to 'n' if you will create directly in the LDAP backend. ['n', 'y']

**CONFIG_KEYSTONE_LDAP_GROUP_ALLOW_UPDATE**
    Set to 'y' if you want to be able to update Keystone groups through the Keystone interface.  Set to 'n' if you will update directly in the LDAP backend. ['n', 'y']

**CONFIG_KEYSTONE_LDAP_GROUP_ALLOW_DELETE**
    Set to 'y' if you want to be able to delete Keystone groups through the Keystone interface.  Set to 'n' if you will delete directly in the LDAP backend. ['n', 'y']

**CONFIG_KEYSTONE_LDAP_GROUP_ADDITIONAL_ATTRIBUTE_MAPPING**
    List of additional LDAP attributes used for mapping additional attribute mappings for groups. Attribute mapping format is <ldap_attr>:<group_attr>, where ldap_attr is the attribute in the LDAP entry and group_attr is the Identity API attribute.

**CONFIG_KEYSTONE_LDAP_USE_TLS**
    Should Keystone LDAP use TLS ['n', 'y']

**CONFIG_KEYSTONE_LDAP_TLS_CACERTDIR**
    Keystone LDAP CA certificate directory

**CONFIG_KEYSTONE_LDAP_TLS_CACERTFILE**
    Keystone LDAP CA certificate file

**CONFIG_KEYSTONE_LDAP_TLS_REQ_CERT**
    Keystone LDAP certificate checking strictness (never, allow, demand) ['never', 'allow', 'demand']

Glance Config parameters
------------------------

**CONFIG_GLANCE_DB_PW**
    The password to use for the Glance to access DB

**CONFIG_GLANCE_KS_PW**
    The password to use for the Glance to authenticate with Keystone

**CONFIG_GLANCE_BACKEND**
    Glance storage backend controls how Glance stores disk images. Supported values: file, swift. Note that Swift installation have to be enabled to have swift backend working. Otherwise Packstack will fallback to 'file'. ['file', 'swift']

Cinder Config parameters
------------------------

**CONFIG_CINDER_DB_PW**
    The password to use for the Cinder to access DB

**CONFIG_CINDER_KS_PW**
    The password to use for the Cinder to authenticate with Keystone

**CONFIG_CINDER_BACKEND**
    The Cinder backend to use, valid options are: lvm, gluster, nfs, vmdk, netapp ['lvm', 'gluster', 'nfs', 'vmdk', 'netapp']

Cinder volume create Config parameters
--------------------------------------

**CONFIG_CINDER_VOLUMES_CREATE**
    Create Cinder's volumes group. This should only be done for testing on a proof-of-concept installation of Cinder. This will create a file-backed volume group and is not suitable for production usage. ['y', 'n']

Cinder volume size Config parameters
------------------------------------

**CONFIG_CINDER_VOLUMES_SIZE**
    Cinder's volumes group size. Note that actual volume size will be extended with 3% more space for VG metadata.

Cinder gluster Config parameters
--------------------------------

**CONFIG_CINDER_GLUSTER_MOUNTS**
    A single or comma separated list of gluster volume shares to mount, eg: ip-address:/vol-name, domain:/vol-name  ['^([\\d]{1,3}\\.){3}[\\d]{1,3}:/.*', '^[a-zA-Z0-9][\\-\\.\\w]*:/.*']

Cinder NFS Config parameters
----------------------------

**CONFIG_CINDER_NFS_MOUNTS**
    A single or comma seprated list of NFS exports to mount, eg: ip-address:/export-name  ['^([\\d]{1,3}\\.){3}[\\d]{1,3}:/.*']

Cinder NetApp main configuration
--------------------------------

**CONFIG_CINDER_NETAPP_LOGIN**
    (required) Administrative user account name used to access the storage system or proxy server.  ['']

**CONFIG_CINDER_NETAPP_PASSWORD**
    (required) Password for the administrative user account specified in the netapp_login parameter. ['']

**CONFIG_CINDER_NETAPP_HOSTNAME**
    (required) The hostname (or IP address) for the storage system or proxy server.

**CONFIG_CINDER_NETAPP_SERVER_PORT**
    (optional) The TCP port to use for communication with ONTAPI on the storage system. Traditionally, port 80 is used for HTTP and port 443 is used for HTTPS; however, this value should be changed if an alternate port has been configured on the storage system or proxy server.  Defaults to 80. ['']

**CONFIG_CINDER_NETAPP_STORAGE_FAMILY**
    (optional) The storage family type used on the storage system; valid values are ontap_7mode for using Data ONTAP operating in 7-Mode or ontap_cluster for using clustered Data ONTAP, or eseries for NetApp E-Series. Defaults to ontap_cluster. ['ontap_7mode', 'ontap_cluster', 'eseries']

**CONFIG_CINDER_NETAPP_TRANSPORT_TYPE**
    (optional) The transport protocol used when communicating with ONTAPI on the storage system or proxy server. Valid values are http or https.  Defaults to http. ['http', 'https']

**CONFIG_CINDER_NETAPP_STORAGE_PROTOCOL**
    (optional) The storage protocol to be used on the data path with the storage system; valid values are iscsi or nfs. Defaults to nfs. ['iscsi', 'nfs']

Cinder NetApp ONTAP-iSCSI configuration
---------------------------------------

**CONFIG_CINDER_NETAPP_SIZE_MULTIPLIER**
    (optional) The quantity to be multiplied by the requested volume size to ensure enough space is available on the virtual storage server (Vserver) to fulfill the volume creation request.  Defaults to 1.0. ['']

Cinder NetApp NFS configuration
-------------------------------

**CONFIG_CINDER_NETAPP_EXPIRY_THRES_MINUTES**
    (optional) This parameter specifies the threshold for last access time for images in the NFS image cache. When a cache cleaning cycle begins, images in the cache that have not been accessed in the last M minutes, where M is the value of this parameter, will be deleted from the cache to create free space on the NFS share. Defaults to 720. ['']

**CONFIG_CINDER_NETAPP_THRES_AVL_SIZE_PERC_START**
    (optional) If the percentage of available space for an NFS share has dropped below the value specified by this parameter, the NFS image cache will be cleaned.  Defaults to 20 ['']

**CONFIG_CINDER_NETAPP_THRES_AVL_SIZE_PERC_STOP**
    (optional) When the percentage of available space on an NFS share has reached the percentage specified by this parameter, the driver will stop clearing files from the NFS image cache that have not been accessed in the last M minutes, where M is the value of the expiry_thres_minutes parameter.  Defaults to 60. ['']

**CONFIG_CINDER_NETAPP_NFS_SHARES**
    (optional) Single or comma-separated list of NetApp NFS shares for Cinder to use.  Format: ip-address:/export-name. Defaults to ''. ['']

**CONFIG_CINDER_NETAPP_NFS_SHARES_CONFIG**
    (optional) File with the list of available NFS shares.   Defaults to '/etc/cinder/shares.conf'. ['']


Cinder NetApp iSCSI & 7-mode configuration
------------------------------------------

**CONFIG_CINDER_NETAPP_VOLUME_LIST**
    (optional) This parameter is only utilized when the storage protocol is configured to use iSCSI. This parameter is used to restrict provisioning to the specified controller volumes. Specify the value of this parameter to be a comma separated list of NetApp controller volume names to be used for provisioning.  Defaults to ''. ['']

**CONFIG_CINDER_NETAPP_VFILER**
    (optional) The vFiler unit on which provisioning of block storage volumes will be done. This parameter is only used by the driver when connecting to an instance with a storage family of Data ONTAP operating in 7-Mode and the storage protocol selected is iSCSI. Only use this parameter when utilizing the MultiStore feature on the NetApp storage system.  Defaults to ''. ['']

Cinder NetApp vServer configuration
-----------------------------------

**CONFIG_CINDER_NETAPP_VSERVER**
    (optional) This parameter specifies the virtual storage server (Vserver) name on the storage cluster on which provisioning of block storage volumes should occur. If using the NFS storage protocol, this parameter is mandatory for storage service catalog support (utilized by Cinder volume type extra_specs support). If this parameter is specified, the exports belonging to the Vserver will only be used for provisioning in the future. Block storage volumes on exports not belonging to the Vserver specified by this  parameter will continue to function normally.  Defaults to ''. ['']

Cinder NetApp E-Series configuration
------------------------------------

**CONFIG_CINDER_NETAPP_CONTROLLER_IPS**
    (optional) This option is only utilized when the storage family is configured to eseries. This option is used to restrict provisioning to the specified controllers. Specify the value of this option to be a comma separated list of controller hostnames or IP addresses to be used for provisioning.  Defaults to ''. ['']

**CONFIG_CINDER_NETAPP_SA_PASSWORD**
    (optional) Password for the NetApp E-Series storage array. Defaults to ''. ['']

**CONFIG_CINDER_NETAPP_WEBSERVICE_PATH**
    (optional) This option is used to specify the path to the E-Series proxy application on a proxy server. The value is combined with the value of the netapp_transport_type, netapp_server_hostname, and netapp_server_port options to create the URL used by the driver to connect to the proxy application.  Defaults to '/devmgr/v2'. ['^[/].*$']

**CONFIG_CINDER_NETAPP_STORAGE_POOLS**
    (optional) This option is used to restrict provisioning to the specified storage pools. Only dynamic disk pools are currently supported. Specify the value of this option to be a comma separated list of disk pool names to be used for provisioning.  Defaults to ''. ['']

Ironic Options
--------------

**CONFIG_IRONIC_DB_PW**
    The password to use for the Ironic DB access

**CONFIG_IRONIC_KS_PW**
    The password to use for Ironic to authenticate with Keystone

Nova Options
------------

**CONFIG_NOVA_DB_PW**
    The password to use for the Nova to access DB

**CONFIG_NOVA_KS_PW**
    The password to use for the Nova to authenticate with Keystone

**CONFIG_NOVA_SCHED_CPU_ALLOC_RATIO**
    The overcommitment ratio for virtual to physical CPUs. Set to 1.0 to disable CPU overcommitment

**CONFIG_NOVA_SCHED_RAM_ALLOC_RATIO**
    The overcommitment ratio for virtual to physical RAM. Set to 1.0 to disable RAM overcommitment

**CONFIG_NOVA_COMPUTE_MIGRATE_PROTOCOL**
    Protocol used for instance migration. Allowed values are tcp and ssh. Note that by defaul nova user is created with /sbin/nologin shell so that ssh protocol won't be working. To make ssh protocol work you have to fix nova user on compute hosts manually. ['tcp', 'ssh']

**CONFIG_NOVA_COMPUTE_MANAGER**
    The manager that will run nova compute.

Nova Network Options
--------------------

**CONFIG_NOVA_COMPUTE_PRIVIF**
    Private interface for Flat DHCP on the Nova compute servers

**CONFIG_NOVA_NETWORK_MANAGER**
    Nova network manager ['^nova\\.network\\.manager\\.\\w+Manager$']

**CONFIG_NOVA_NETWORK_PUBIF**
    Public interface on the Nova network server

**CONFIG_NOVA_NETWORK_PRIVIF**
    Private interface for network manager on the Nova network server

**CONFIG_NOVA_NETWORK_FIXEDRANGE**
    IP Range for network manager ['^[\\:\\.\\da-fA-f]+(\\/\\d+){0,1}$']

**CONFIG_NOVA_NETWORK_FLOATRANGE**
    IP Range for Floating IP's ['^[\\:\\.\\da-fA-f]+(\\/\\d+){0,1}$']

**CONFIG_NOVA_NETWORK_AUTOASSIGNFLOATINGIP**
    Automatically assign a floating IP to new instances ['y', 'n']

Nova Network VLAN Options
-------------------------

**CONFIG_NOVA_NETWORK_VLAN_START**
    First VLAN for private networks

**CONFIG_NOVA_NETWORK_NUMBER**
    Number of networks to support

**CONFIG_NOVA_NETWORK_SIZE**
    Number of addresses in each private subnet

Neutron config
--------------

**CONFIG_NEUTRON_KS_PW**
    The password to use for Neutron to authenticate with Keystone

**CONFIG_NEUTRON_DB_PW**
    The password to use for Neutron to access DB

**CONFIG_NEUTRON_L3_EXT_BRIDGE**
    The name of the ovs bridge (or empty for linuxbridge) that the Neutron L3 agent will use for external  traffic, or 'provider' using provider networks.

**CONFIG_NEUTRON_METADATA_PW**
    Neutron metadata agent password

**CONFIG_LBAAS_INSTALL**
    Set to 'y' if you would like Packstack to install Neutron LBaaS ['y', 'n']

**CONFIG_NEUTRON_METERING_AGENT_INSTALL**
    Set to 'y' if you would like Packstack to install Neutron L3 Metering agent ['y', 'n']

**CONFIG_NEUTRON_FWAAS**
    Whether to configure neutron Firewall as a Service ['y', 'n']

Neutron ML2 plugin config
-------------------------

**CONFIG_NEUTRON_ML2_TYPE_DRIVERS**
    A comma separated list of network type driver entrypoints to be loaded from the neutron.ml2.type_drivers namespace. ['local', 'flat', 'vlan', 'gre', 'vxlan']

**CONFIG_NEUTRON_ML2_TENANT_NETWORK_TYPES**
    A comma separated ordered list of network_types to allocate as tenant networks. The value 'local' is only useful for single-box testing but provides no connectivity between hosts. ['local', 'vlan', 'gre', 'vxlan']

**CONFIG_NEUTRON_ML2_MECHANISM_DRIVERS**
    A comma separated ordered list of networking mechanism driver entrypoints to be loaded from the neutron.ml2.mechanism_drivers namespace. ['logger', 'test', 'linuxbridge', 'openvswitch', 'hyperv', 'ncs', 'arista', 'cisco_nexus', 'l2population']

**CONFIG_NEUTRON_ML2_FLAT_NETWORKS**
    A comma separated  list of physical_network names with which flat networks can be created. Use * to allow flat networks with arbitrary physical_network names.

**CONFIG_NEUTRON_ML2_VLAN_RANGES**
    A comma separated list of <physical_network>:<vlan_min>:<vlan_max> or <physical_network> specifying physical_network names usable for VLAN provider and tenant networks, as well as ranges of VLAN tags on each available for allocation to tenant networks.

**CONFIG_NEUTRON_ML2_TUNNEL_ID_RANGES**
    A comma separated list of <tun_min>:<tun_max> tuples enumerating ranges of GRE tunnel IDs that are available for tenant network allocation. Should be an array with tun_max +1 - tun_min > 1000000

**CONFIG_NEUTRON_ML2_VXLAN_GROUP**
    Multicast group for VXLAN. If unset, disables VXLAN enable sending allocate broadcast traffic to this multicast group. When left unconfigured, will disable multicast VXLAN mode. Should be an Multicast IP (v4 or v6) address.

**CONFIG_NEUTRON_ML2_VNI_RANGES**
    A comma separated list of <vni_min>:<vni_max> tuples enumerating ranges of VXLAN VNI IDs that are available for tenant network allocation. Min value is 0 and Max value is 16777215.

**CONFIG_NEUTRON_L2_AGENT**
    The name of the L2 agent to be used with Neutron ['linuxbridge', 'openvswitch']

Neutron LB agent config
-----------------------

**CONFIG_NEUTRON_LB_INTERFACE_MAPPINGS**
    A comma separated list of interface mappings for the Neutron linuxbridge plugin (eg. physnet1:eth1,physnet2:eth2,physnet3:eth3)

Neutron OVS agent config
------------------------

**CONFIG_NEUTRON_OVS_BRIDGE_MAPPINGS**
    A comma separated list of bridge mappings for the Neutron openvswitch plugin (eg. physnet1:br-eth1,physnet2:br-eth2,physnet3:br-eth3)

**CONFIG_NEUTRON_OVS_BRIDGE_IFACES**
    A comma separated list of colon-separated OVS bridge:interface pairs. The interface will be added to the associated bridge.

Neutron OVS agent config for tunnels
------------------------------------

**CONFIG_NEUTRON_OVS_TUNNEL_IF**
    The interface for the OVS tunnel. Packstack will override the IP address used for tunnels on this hypervisor to the IP found on the specified interface. (eg. eth1)

Neutron OVS agent config for VXLAN
----------------------------------

**CONFIG_NEUTRON_OVS_VXLAN_UDP_PORT**
    VXLAN UDP port

NOVACLIENT Config parameters
----------------------------

OpenStack Horizon Config parameters
-----------------------------------

**CONFIG_HORIZON_SSL**
    To set up Horizon communication over https set this to 'y' ['y', 'n']

SSL Config parameters
---------------------

**CONFIG_SSL_CERT**
    PEM encoded certificate to be used for ssl on the https server, leave blank if one should be generated, this certificate should not require a passphrase

**CONFIG_SSL_KEY**
    SSL keyfile corresponding to the certificate if one was entered

**CONFIG_SSL_CACHAIN**
    PEM encoded CA certificates from which the certificate chain of the server certificate can be assembled.

OpenStack Swift Config parameters
---------------------------------

**CONFIG_SWIFT_KS_PW**
    The password to use for the Swift to authenticate with Keystone

**CONFIG_SWIFT_STORAGES**
    A comma separated list of devices which to use as Swift Storage device. Each entry should take the format /path/to/dev, for example /dev/vdb will install /dev/vdb as Swift storage device (packstack does not create the filesystem, you must do this first). If value is omitted Packstack will create a loopback device for test setup

**CONFIG_SWIFT_STORAGE_ZONES**
    Number of swift storage zones, this number MUST be no bigger than the number of storage devices configured

**CONFIG_SWIFT_STORAGE_REPLICAS**
    Number of swift storage replicas, this number MUST be no bigger than the number of storage zones configured

**CONFIG_SWIFT_STORAGE_FSTYPE**
    FileSystem type for storage nodes ['xfs', 'ext4']

**CONFIG_SWIFT_HASH**
    Shared secret for Swift

**CONFIG_SWIFT_STORAGE_SIZE**
    Size of the swift loopback file storage device

Heat Config parameters
----------------------

**CONFIG_HEAT_DB_PW**
    The password used by Heat user to authenticate against DB

**CONFIG_HEAT_AUTH_ENC_KEY**
    The encryption key to use for authentication info in database (16, 24, or 32 chars)

**CONFIG_HEAT_KS_PW**
    The password to use for the Heat to authenticate with Keystone

**CONFIG_HEAT_CLOUDWATCH_INSTALL**
    Set to 'y' if you would like Packstack to install Heat CloudWatch API ['y', 'n']

**CONFIG_HEAT_CFN_INSTALL**
    Set to 'y' if you would like Packstack to install Heat CloudFormation API ['y', 'n']

**CONFIG_HEAT_DOMAIN**
    Name of Keystone domain for Heat

**CONFIG_HEAT_DOMAIN_ADMIN**
    Name of Keystone domain admin user for Heat

**CONFIG_HEAT_DOMAIN_PASSWORD**
    Password for Keystone domain admin user for Heat

Provisioning demo config
------------------------

**CONFIG_PROVISION_DEMO**
    Whether to provision for demo usage and testing. Note that provisioning is only supported for all-in-one installations. ['y', 'n']

**CONFIG_PROVISION_TEMPEST**
    Whether to configure tempest for testing ['y', 'n']

Provisioning demo config
------------------------

**CONFIG_PROVISION_DEMO_FLOATRANGE**
    The CIDR network address for the floating IP subnet

**CONFIG_PROVISION_CIRROS_URL**
    A URL or local file location for the Cirros demo image used for Glance

Provisioning tempest config
---------------------------

**CONFIG_PROVISION_TEMPEST_USER**
    The name of the Tempest Provisioning user. If you don't provide a user name, Tempest will be configured in a standalone mode

**CONFIG_PROVISION_TEMPEST_USER_PW**
    The password to use for the Tempest Provisioning user

**CONFIG_PROVISION_TEMPEST_FLOATRANGE**
    The CIDR network address for the floating IP subnet

**CONFIG_PROVISION_TEMPEST_REPO_URI**
    The uri of the tempest git repository to use

**CONFIG_PROVISION_TEMPEST_REPO_REVISION**
    The revision of the tempest git repository to use

Provisioning all-in-one ovs bridge config
-----------------------------------------

**CONFIG_PROVISION_ALL_IN_ONE_OVS_BRIDGE**
    Whether to configure the ovs external bridge in an all-in-one deployment ['y', 'n']

Ceilometer Config parameters
----------------------------

**CONFIG_CEILOMETER_SECRET**
    Secret key for signing metering messages

**CONFIG_CEILOMETER_KS_PW**
    The password to use for Ceilometer to authenticate with Keystone

**CONFIG_CEILOMETER_COORDINATION_BACKEND**
    Backend driver for group membership coordination ['redis', 'none']

MONGODB Config parameters
-------------------------

**CONFIG_MONGODB_HOST**
    The IP address of the server on which to install MongoDB

Redis Config parameters
-----------------------

**CONFIG_REDIS_MASTER_HOST**
    The IP address of the server on which to install redis master server

**CONFIG_REDIS_PORT**
    The port on which the redis server(s) listens

**CONFIG_REDIS_HA**
    Should redis try to use HA ['y', 'n']

**CONFIG_REDIS_SLAVE_HOSTS**
    The hosts on which to install redis slaves

**CONFIG_REDIS_SENTINEL_HOSTS**
    The hosts on which to install redis sentinel servers

**CONFIG_REDIS_SENTINEL_CONTACT_HOST**
    The host to configure as the coordination sentinel

**CONFIG_REDIS_SENTINEL_PORT**
    The port on which redis sentinel servers listen

**CONFIG_REDIS_SENTINEL_QUORUM**
    The quorum value for redis sentinel servers

**CONFIG_REDIS_MASTER_NAME**
    The name of the master server watched by the sentinel ['[a-z]+']

Sahara Config parameters
------------------------

**CONFIG_SAHARA_DB_PW**
    The password to use for the Sahara DB access

**CONFIG_SAHARA_KS_PW**
    The password to use for Sahara to authenticate with Keystone

Trove config parameters
-----------------------

**CONFIG_TROVE_DB_PW**
    The password to use for the Trove DB access

**CONFIG_TROVE_KS_PW**
    The password to use for Trove to authenticate with Keystone

**CONFIG_TROVE_NOVA_USER**
    The user to use when Trove connects to Nova

**CONFIG_TROVE_NOVA_TENANT**
    The tenant to use when Trove connects to Nova

**CONFIG_TROVE_NOVA_PW**
    The password to use when Trove connects to Nova

Nagios Config parameters
------------------------

**CONFIG_NAGIOS_PW**
    The password of the nagiosadmin user on the Nagios server

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
