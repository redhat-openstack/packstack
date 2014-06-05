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
- packstack --gen-answer-file=<file>  / packstack --answer-file=<file>

The third option allows the user to generate a default answer file, edit the default options and finally run Packstack a second time using this answer file. This is the easiest way to run Packstack and the one that will be documented here. When <file> is created the OPTIONS below will be contained and can be edited by the user.

OPTIONS
=======

Global Options
--------------

**CONFIG_GLANCE_INSTALL**
    Set to 'y' if you would like Packstack to install Glance ['y', 'n'].

**CONFIG_CINDER_INSTALL**
    Set to 'y' if you would like Packstack to install Cinder ['y', 'n'].

**CONFIG_NOVA_INSTALL**
    Set to 'y' if you would like Packstack to install Nova ['y', 'n'].

**CONFIG_HORIZON_INSTALL**
    Set to 'y' if you would like Packstack to install Horizon ['y', 'n'].

**CONFIG_SWIFT_INSTALL**
    Set to 'y' if you would like Packstack to install Swift ['y', 'n'].

**CONFIG_CLIENT_INSTALL**
    Set to 'y' if you would like Packstack to install the OpenStack Client packages. An admin "rc" file will also be installed ['y', 'n'].

**CONFIG_NTP_SERVERS**
    Comma separated list of NTP servers. Leave plain if Packstack should not install ntpd on instances..

**CONFIG_NAGIOS_INSTALL**
    Set to 'y' if you would like Packstack to install Nagios to monitor openstack hosts ['y', 'n'].

**CONFIG_CEILOMETER_INSTALL**
    Set to 'y' if you would like Packstack to install OpenStack Metering (Ceilometer).

**CONFIG_HEAT_INSTALL**
    Set to 'y' if you would like Packstack to install OpenStack Orchestration (Heat).

**CONFIG_NEUTRON_INSTALL**
    Set to 'y' if you would like Packstack to install OpenStack Networking (Neutron).

**CONFIG_MARIADB_INSTALL**
    Set to 'y' if you would like Packstack to install MariaDB.

**CONFIG_CONTROLLER_HOST**
    The IP address of the server on which to install OpenStack services specific to controller role such as API servers, Horizon, etc. This parameter replaced following deprecated parameters: CONFIG_CEILOMETER_HOST, CONFIG_CINDER_HOST, CONFIG_GLANCE_HOST, CONFIG_HORIZON_HOST, CONFIG_HEAT_HOST, CONFIG_KEYSTONE_HOST, CONFIG_NAGIOS_HOST, CONFIG_NEUTRON_SERVER_HOST, CONFIG_NEUTRON_LBAAS_HOSTS, CONFIG_NOVA_API_HOST, CONFIG_NOVA_CERT_HOST, CONFIG_NOVA_VNCPROXY_HOST, CONFIG_NOVA_SCHED_HOST, CONFIG_OSCLIENT_HOST, CONFIG_SWIFT_PROXY_HOSTS.

**CONFIG_COMPUTE_HOSTS**
    The list of IP addresses of the server on which to install the Nova compute service. This parameter replaced following deprecated parameters: CONFIG_NOVA_COMPUTE_HOSTS.

**CONFIG_NETWORK_HOSTS**
    The list of IP addresses of the server on which to install the network service such as Nova network or Neutron. This parameter replaced following deprecated parameters: CONFIG_NEUTRON_L3_HOSTS, CONFIG_NEUTRON_DHCP_HOSTS, CONFIG_NEUTRON_METADATA_HOSTS, CONFIG_NOVA_NETWORK_HOSTS.


SSH Configs
------------

**CONFIG_SSH_KEY**
    Path to a Public key to install on servers. If a usable key has not been installed on the remote servers the user will be prompted for a password and this key will be installed so the password will not be required again.

MariaDB Config parameters
-----------------------

**CONFIG_MARIADB_HOST**
    The IP address of the server on which to install MariaDB.

**CONFIG_MARIADB_USER**
    Username for the MariaDB admin user.

**CONFIG_MARIADB_PW**
    Password for the MariaDB admin user.

AMQP Config parameters
----------------------


**CONFIG_AMQP_BACKEND**
    Set the AMQP service backend. Allowed values are: qpid, rabbitmq

**CONFIG_AMQP_HOST**
    The IP address of the server on which to install the QPID service.

**CONFIG_AMQP_ENABLE_SSL**
    Enable SSL for the QPID service.

**CONFIG_AMQP_NSS_CERTDB_PW**
    The password for the NSS certificate database of the QPID service.

**CONFIG_AMQP_SSL_PORT**
    The port in which the QPID service listens to SSL connections.

**CONFIG_AMQP_SSL_CERT_FILE**
    The filename of the certificate that the QPID service is going to use.

**CONFIG_AMQP_SSL_KEY_FILE**
    The filename of the private key that the QPID service is going to use.

**CONFIG_AMQP_SSL_SELF_SIGNED**
    Auto Generates self signed SSL certificate and key.

**CONFIG_AMQP_ENABLE_AUTH**
    Enable Authentication for the AMQP service

**CONFIG_AMQP_AUTH_USER**
    User for amqp authentication

**CONFIG_AMQP_AUTH_PASSWORD**
    Password for user authentication


Keystone Config parameters
--------------------------

**CONFIG_KEYSTONE_DB_PW**
    The password to use for the Keystone to access DB.

**CONFIG_KEYSTONE_ADMIN_TOKEN**
    The token to use for the Keystone service api.

**CONFIG_KEYSTONE_ADMIN_PW**
    The password to use for the Keystone admin user.

**CONFIG_KEYSTONE_DEMO_PW**
    The password to use for the Keystone demo user

**CONFIG_KEYSTONE_TOKEN_FORMAT**
    Kestone token format. Use either UUID or PKI

Glance Config parameters
------------------------

**CONFIG_GLANCE_DB_PW**
    The password to use for the Glance to access DB.

**CONFIG_GLANCE_KS_PW**
    The password to use for the Glance to authenticate with Keystone.

Cinder Config parameters
------------------------

**CONFIG_CINDER_DB_PW**
    The password to use for the Cinder to access DB.

**CONFIG_CINDER_KS_PW**
    The password to use for the Cinder to authenticate with Keystone.

**CONFIG_CINDER_BACKEND**
    The Cinder backend to use ['lvm', 'gluster', 'nfs', 'vmdk', 'netapp'].

Cinder volume create Config parameters
--------------------------------------

**CONFIG_CINDER_VOLUMES_CREATE**
    Create Cinder's volumes group ['y', 'n'].

Cinder volume size Config parameters
------------------------------------

**CONFIG_CINDER_VOLUMES_SIZE**
    Cinder's volumes group size.

Cinder gluster Config parameters
--------------------------------

**CONFIG_CINDER_GLUSTER_MOUNTS**
    A single or comma separated list of gluster volume shares.

Cinder NFS Config parameters
----------------------------

**CONFIG_CINDER_NFS_MOUNTS**
    A single or comma separated list of NFS exports to mount.

Cinder NetApp Config parameters
----------------------------

**CONFIG_CINDER_NETAPP_LOGIN**
    (required) Password for the administrative user account specified in the netapp_login parameter.

**CONFIG_CINDER_NETAPP_PASSWORD**
    (required) The hostname (or IP address) for the storage system or proxy server.

**CONFIG_CINDER_NETAPP_HOSTNAME**
    (required) The hostname (or IP address) for the storage system or proxy server.

**CONFIG_CINDER_NETAPP_SERVER_PORT**
    (optional) The TCP port to use for communication with ONTAPI on the storage system. Traditionally, port 80 is used for HTTP and port 443 is used for HTTPS; however, this value should be changed if an alternate port has been configured on the storage system or proxy server.  Defaults to 80

**CONFIG_CINDER_NETAPP_STORAGE_FAMILY**
    (optional) The storage family type used on the storage system; valid values are ontap_7mode for using Data ONTAP operating in 7-Mode or ontap_cluster for using clustered Data ONTAP, or eseries for NetApp E-Series.  Defaults to ontap_cluster.

**CONFIG_CINDER_NETAPP_TRANSPORT_TYPE**
    (optional) The transport protocol used when communicating with ONTAPI on the storage system or proxy server. Valid values are http or https. Defaults to http.

**CONFIG_CINDER_NETAPP_STORAGE_PROTOCOL**
    (optional) The storage protocol to be used on the data path with the storage system; valid values are iscsi or nfs. Defaults to nfs.

**CONFIG_CINDER_NETAPP_SIZE_MULTIPLIER**
    (optional) The quantity to be multiplied by the requested volume size to ensure enough space is available on the virtual storage server (Vserver) to fulfill the volume creation request. Defaults to 1.0.

**CONFIG_CINDER_NETAPP_EXPIRY_THRES_MINUTES**
    (optional) This parameter specifies the threshold for last access time for images in the NFS image cache. When a cache cleaning cycle begins, images in the cache that have not been accessed in the last M minutes, where M is the value of this parameter, will be deleted from the cache to create free space on the NFS share. Defaults to 720.

**CONFIG_CINDER_NETAPP_THRES_AVL_SIZE_PERC_START**
    (optional) If the percentage of available space for an NFS share has dropped below the value specified by this parameter, the NFS image cache will be cleaned. Defaults to 20.

**CONFIG_CINDER_NETAPP_THRES_AVL_SIZE_PERC_STOP**
    (optional) When the percentage of available space on an NFS share has reached the percentage specified by this parameter, the driver will stop clearing files from the NFS image cache that have not been accessed in the last M minutes, where M is the value of the expiry_thres_minutes parameter.  Defaults to 60.

**CONFIG_CINDER_NETAPP_NFS_SHARES_CONFIG**
    (optional) File with the list of available NFS shares.  Defaults to ''.

**CONFIG_CINDER_NETAPP_VOLUME_LIST**
    (optional) This parameter is only utilized when the storage protocol is configured to use iSCSI. This parameter is used to restrict provisioning to the specified controller volumes. Specify the value of this parameter to be a comma separated list of NetApp controller volume names to be used for provisioning.  Defaults to ''.

**CONFIG_CINDER_NETAPP_VFILER**
    (optional) The vFiler unit on which provisioning of block storage volumes will be done. This parameter is only used by the driver when connecting to an instance with a storage family of Data ONTAP operating in 7-Mode and the storage protocol selected is iSCSI. Only use this parameter when utilizing the MultiStore feature on the NetApp storage system.  Defaults to ''.

**CONFIG_CINDER_NETAPP_VSERVER**
    (optional) This parameter specifies the virtual storage server (Vserver) name on the storage cluster on which provisioning of block storage volumes should occur. If using the NFS storage protocol, this parameter is mandatory for storage service catalog support (utilized by Cinder volume type extra_specs support). If this parameter is specified, the exports belonging to the Vserver will only be used for provisioning in the future. Block storage volumes on exports not belonging to the Vserver specified by this parameter will continue to function normally. Defaults to ''.

**CONFIG_CINDER_NETAPP_CONTROLLER_IPS**
    (optional) This option is only utilized when the storage family is configured to eseries. This option is used to restrict provisioning to the specified controllers. Specify the value of this option to be a comma separated list of controller hostnames or IP addresses to be used for provisioning. Defaults to ''.

**CONFIG_CINDER_NETAPP_SA_PASSWORD**
    (optional) Password for the NetApp E-Series storage array. Defaults to ''.

**CONFIG_CINDER_NETAPP_WEBSERVICE_PATH**
    (optional) This option is used to specify the path to the E-Series proxy application on a proxy server. The value is combined with the value of the netapp_transport_type, netapp_server_hostname, and netapp_server_port options to create the URL used by the driver to connect to the proxy application.  Defaults to '/devmgr/v2'.

**CONFIG_CINDER_NETAPP_STORAGE_POOLS**
    (optional) This option is used to restrict provisioning to the specified storage pools. Only dynamic disk pools are currently supported. Specify the value of this option to be a comma separated list of disk pool names to be used for provisioning. Defaults to ''.


Nova Options
------------

**CONFIG_NOVA_COMPUTE_PRIVIF**
    Private interface for Flat DHCP on the Nova compute servers.

**CONFIG_NOVA_COMPUTE_MIGRATE_PROTOCOL**
    Protocol used for instance migration. Allowed values are tcp and ssh. Note that by defaul nova user is created with /sbin/nologin shell so that ssh protocol won't be working. To make ssh protocol work you have to fix nova user on compute hosts manually.

**CONFIG_NOVA_NETWORK_HOSTS**
    List of IP address of the servers on which to install the Nova Network service.

**CONFIG_NOVA_DB_PW**
    The password to use for the Nova to access DB.

**CONFIG_NOVA_KS_PW**
    The password to use for the Nova to authenticate with Keystone.

**CONFIG_NOVA_NETWORK_PUBIF**
    Public interface on the Nova network server.

**CONFIG_NOVA_NETWORK_PRIVIF**
    Private interface for Flat DHCP on the Nova network server.

**CONFIG_NOVA_NETWORK_FIXEDRANGE**
    IP Range for Flat DHCP ['^([\\d]{1,3}\\.){3}[\\d]{1,3}/\\d\\d?$'].

**CONFIG_NOVA_NETWORK_FLOATRANGE**
    IP Range for Floating IP's ['^([\\d]{1,3}\\.){3}[\\d]{1,3}/\\d\\d?$'].

**CONFIG_NOVA_SCHED_HOST**
    The IP address of the server on which to install the Nova Scheduler service.

**CONFIG_NOVA_SCHED_CPU_ALLOC_RATIO**
    The overcommitment ratio for virtual to physical CPUs. Set to 1.0 to disable CPU overcommitment.

**CONFIG_NOVA_SCHED_RAM_ALLOC_RATIO**
    The overcommitment ratio for virtual to physical RAM. Set to 1.0 to disable RAM overcommitment.

**CONFIG_NOVA_CONDUCTOR_HOST**
    The IP address of the server on which to install the Nova Conductor service.

**CONFIG_NOVA_NETWORK_AUTOASSIGNFLOATINGIP**
    Automatically assign a floating IP to new instances.

**CONFIG_NOVA_NETWORK_DEFAULTFLOATINGPOOL**
    Name of the default floating pool to which the specified floating ranges are added to.

**CONFIG_NOVA_NETWORK_MANAGER**
    Nova network manager.

**CONFIG_NOVA_NETWORK_NUMBER**
    Number of networks to support.

**CONFIG_NOVA_NETWORK_SIZE**
    Number of addresses in each private subnet.

**CONFIG_NOVA_NETWORK_VLAN_START**
    First VLAN for private networks.

OpenStack Horizon Config parameters
-----------------------------------

**CONFIG_HORIZON_SSL**
    To set up Horizon communication over https set this to "y" ['y', 'n'].

**CONFIG_SSL_CERT**
    PEM encoded certificate to be used for ssl on the https server, leave blank if one should be generated, this certificate should not require a passphrase.

**CONFIG_SSL_KEY**
    Keyfile corresponding to the certificate if one was entered.

**CONFIG_SSL_CACHAIN**
    PEM encoded CA certificates from which the certificate chain of the server certificate can be assembled.

OpenStack Swift Config parameters
---------------------------------

**CONFIG_SWIFT_KS_PW**
    The password to use for the Swift to authenticate with Keystone.

**CONFIG_SWIFT_STORAGES**
    A comma separated list of devices which to use as Swift Storage device. Each entry should take the format /path/to/dev, for example /dev/vdb will install /dev/vdb as Swift storage device (packstack does not create the filesystem, you must do this first). If value is omitted Packstack will create a loopback device for test setup

**CONFIG_SWIFT_STORAGE_ZONES**
    Number of swift storage zones, this number MUST be no bigger than the number of storage devices configured.

**CONFIG_SWIFT_STORAGE_REPLICAS**
    Number of swift storage replicas, this number MUST be no bigger than the number of storage zones configured.

**CONFIG_SWIFT_STORAGE_FSTYPE**
    FileSystem type for storage nodes ['xfs', 'ext4'].

**CONFIG_SWIFT_HASH**
    Shared secret for Swift.

Server Prepare Configs
----------------------

**CONFIG_USE_EPEL**
    Install OpenStack from EPEL. If set to "y" EPEL will be installed on each server ['y', 'n'].

**CONFIG_REPO**
    A comma separated list of URLs to any additional yum repositories to install.

**CONFIG_RH_USER**
    To subscribe each server with Red Hat subscription manager, include this with **CONFIG_RH_PW**.

**CONFIG_RH_PW**
    To subscribe each server with Red Hat subscription manager, include this with **CONFIG_RH_USER**.

**CONFIG_RH_BETA_REPO**
    To subscribe each server with Red Hat subscription manager, to Red Hat Beta RPM's ['y', 'n'].

**CONFIG_SATELLITE_URL**
    To subscribe each server with RHN Satellite,fill Satellite's URL here. Note that either satellite's username/password or activation key has to be provided.

RHN Satellite config
--------------------

**CONFIG_SATELLITE_USER**
    Username to access RHN Satellite.

**CONFIG_SATELLITE_PW**
    Password to access RHN Satellite.

**CONFIG_SATELLITE_AKEY**
    Activation key for subscription to RHN Satellite.

**CONFIG_SATELLITE_CACERT**
    Specify a path or URL to a SSL CA certificate to use.

**CONFIG_SATELLITE_PROFILE**
    If required specify the profile name that should be used as an identifier for the system in RHN Satellite.

**CONFIG_SATELLITE_FLAGS**
    Comma separated list of flags passed to rhnreg_ks. Valid flags are: novirtinfo, norhnsd, nopackages ['novirtinfo', 'norhnsd', 'nopackages'].

**CONFIG_SATELLITE_PROXY**
    Specify a HTTP proxy to use with RHN Satellite.

RHN Satellite proxy config
--------------------------

**CONFIG_SATELLITE_PROXY_USER**
    Specify a username to use with an authenticated HTTP proxy.

**CONFIG_SATELLITE_PROXY_PW**
    Specify a password to use with an authenticated HTTP proxy.

Nagios Config parameters
------------------------

**CONFIG_NAGIOS_PW**
    The password of the nagiosadmin user on the Nagios server.

Ceilometer Config Parameters
----------------------------

**CONFIG_CEILOMETER_SECRET**
    Secret key for signing metering messages.

**CONFIG_CEILOMETER_KS_PW**
    The password to use for Ceilometer to authenticate with Keystone.

Heat Config Parameters
----------------------

**CONFIG_HEAT_DB_PW**
    The password used by Heat user to authenticate against MariaDB.

**CONFIG_HEAT_AUTH_ENC_KEY**
    The encryption key to use for authentication info in database.

**CONFIG_HEAT_KS_PW**
    The password to use for the Heat to authenticate with Keystone.

**CONFIG_HEAT_USING_TRUSTS**
    Set to 'y' if you would like Packstack to install heat with trusts as deferred auth method.  If not, the stored password method will be used.

**CONFIG_HEAT_CLOUDWATCH_INSTALL**
    Set to 'y' if you would like Packstack to install Heat CloudWatch API.

**CONFIG_HEAT_CFN_INSTALL**
    Set to 'y' if you would like Packstack to install Heat CloudFormation API.

**CONFIG_HEAT_DOMAIN**
    Name of Keystone domain for Heat. By default, the value is **heat**.

**CONFIG_HEAT_DOMAIN_ADMIN**
    Name of Keystone domain admin user for Heat. By default, the value is **heat_admin**.

**CONFIG_HEAT_DOMAIN_PASSWORD**
    Password for Keystone domain admin user for Heat.

Neutron Config Parameters
-------------------------

**CONFIG_NEUTRON_KS_PW**
    The password to use for Neutron to authenticate with Keystone.

**CONFIG_NEUTRON_DB_PW**
    The password to use for Neutron to access DB.

**CONFIG_NEUTRON_L3_EXT_BRIDGE**
    The name of the bridge that the Neutron L3 agent will use for external traffic, or 'provider' if using provider networks.

**CONFIG_NEUTRON_L2_PLUGIN**
    The name of the L2 plugin to be used with Neutron. (eg. linuxbridge, openvswitch, ml2).

**CONFIG_NEUTRON_METADATA_PW**
    A comma separated list of IP addresses on which to install Neutron metadata agent.

**CONFIG_NEUTRON_FWAAS**
    Whether to configure neutron Firewall as a Service.

**CONFIG_NEUTRON_LB_TENANT_NETWORK_TYPE**
    The type of network to allocate for tenant networks (eg. vlan, local, gre).

**CONFIG_NEUTRON_LB_VLAN_RANGES**
    A comma separated list of VLAN ranges for the Neutron linuxbridge plugin (eg. physnet1:1:4094,physnet2,physnet3:3000:3999).

**CONFIG_NEUTRON_LB_INTERFACE_MAPPINGS**
    A comma separated list of interface mappings for the Neutron linuxbridge plugin (eg. physnet1:br-eth1,physnet2:br-eth2,physnet3:br-eth3).

**CONFIG_NEUTRON_OVS_TENANT_NETWORK_TYPE**
    Type of network to allocate for tenant networks (eg. vlan, local, gre).

**CONFIG_NEUTRON_OVS_VLAN_RANGES**
    A comma separated list of VLAN ranges for the Neutron openvswitch plugin (eg. physnet1:1:4094,physnet2,physnet3:3000:3999).

**CONFIG_NEUTRON_OVS_BRIDGE_MAPPINGS**
    A comma separated list of bridge mappings for the Neutron openvswitch plugin (eg. physnet1:br-eth1,physnet2:br-eth2,physnet3:br-eth3).

**CONFIG_NEUTRON_OVS_BRIDGE_IFACES**
    A comma separated list of colon-separated OVS brid.

**CONFIG_NEUTRON_OVS_TUNNEL_RANGES**
    A comma separated list of tunnel ranges for the Neutron openvswitch plugin.

**CONFIG_NEUTRON_OVS_TUNNEL_IF**
    Override the IP used for GRE tunnels on this hypervisor to the IP found on the specified interface (defaults to the HOST IP).

**CONFIG_NEUTRON_ML2_TYPE_DRIVERS**
    A comma separated list of network type (eg: local, flat, vlan, gre, vxlan).

**CONFIG_NEUTRON_ML2_TENANT_NETWORK_TYPES**
    A comma separated ordered list of network_types to allocate as tenant networks (eg: local, flat, vlan, gre, vxlan). The value 'local' is only useful for single-box testing but provides no connectivity between hosts.

**CONFIG_NEUTRON_ML2_SM_DRIVERS**
    A comma separated ordered list of networking mechanism driver entrypoints to be loaded from the **neutron.ml2.mechanism_drivers** namespace (eg: logger, test, linuxbridge, openvswitch, hyperv, ncs, arista, cisco_nexus, l2population).

**CONFIG_NEUTRON_ML2_FLAT_NETWORKS**
    A comma separated list of physical_network names with which flat networks can be created. Use * to allow flat networks with arbitrary physical_network names.

**CONFIG_NEUTRON_ML2_VLAN_RANGES**
    A comma separated list of **<physical_network>:<vlan_min>:<vlan_max>** or **<physical_network>** specifying physical_network names usable for VLAN provider and tenant networks, as well as ranges of VLAN tags on each available for allocation to tenant networks.

**CONFIG_NEUTRON_ML2_TUNNEL_ID_RANGES**
    A comma separated list of **<tun_min>:<tun_max>** tuples enumerating ranges of GRE tunnel IDs that are available for tenant network allocation. Should be an array with **tun_max +1 - tun_min > 1000000**.

**CONFIG_NEUTRON_ML2_VXLAN_GROUP**
    Multicast group for VXLAN. If unset, disables VXLAN enable sending allocate broadcast traffic to this multicast group. When left unconfigured, will disable multicast VXLAN mode. Should be an **Multicast IP (v4 or v6)** address.

**CONFIG_NEUTRON_ML2_VNI_RANGES**
    A comma separated list of **<vni_min>:<vni_max>** tuples enumerating ranges of VXLAN VNI IDs that are available for tenant network allocation. Min value is 0 and Max value is 16777215.


Provision Config Parameters
---------------------------

**CONFIG_PROVISION_ALL_IN_ONE_OVS_BRIDGE**
    Whether to configure the ovs external bridge in an all-in-one deployment.

**CONFIG_PROVISION_DEMO**
    Whether to provision for demo usage and testing.

**CONFIG_PROVISION_DEMO_FLOATRANGE**
    The CIDR network address for the floating IP subnet.

**CONFIG_PROVISION_TEMPEST**
    Whether to configure tempest for testing.

**CONFIG_PROVISION_TEMPEST_USER**
    The name of the Tempest Provisioning user. If you don't provide a user name, Tempest will be configured in a standalone mode. If you choose the **demo** user, packstack will use the password from **CONFIG_KEYSTONE_DEMO_PW** if **CONFIG_PROVISION_DEMO** is enabled. If not, the **CONFIG_PROVISION_TEMPEST_USER_PW** will be used.

**CONFIG_PROVISION_TEMPEST_USER_PW**
    The password to use for the Tempest Provisioning user.

**CONFIG_PROVISION_TEMPEST_REPO_REVISION**
    The revision of the tempest git repository to use.

**CONFIG_PROVISION_TEMPEST_REPO_URI**
    The uri of the tempest git repository to use.


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
