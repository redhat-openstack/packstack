#package { 'nfs-utils': ensure => present }
#package { 'open-iscsi-utils': ensure => present }

if "%(CONFIG_CINDER_NETAPP_STORAGE_PROTOCOL)s" == "nfs" {
    $storage_package = 'nfs-utils'
}
elsif "%(CONFIG_CINDER_NETAPP_STORAGE_PROTOCOL)s" == "iscsi" {
   $storage_package = 'open-iscsi-utils'
}

class { 'cinder::volume::netapp':
    netapp_login => "%(CONFIG_CINDER_NETAPP_LOGIN)s",
    netapp_password => "%(CONFIG_CINDER_NETAPP_PASSWORD)s",
    netapp_server_hostname => "%(CONFIG_CINDER_NETAPP_HOSTNAME)s",
    netapp_server_port => "%(CONFIG_CINDER_NETAPP_SERVER_PORT)s",  #d
    netapp_size_multiplier => "%(CONFIG_CINDER_NETAPP_SIZE_MULTIPLIER)s", #f
    netapp_storage_family => "%(CONFIG_CINDER_NETAPP_STORAGE_FAMILY)s",
    netapp_storage_protocol => "%(CONFIG_CINDER_NETAPP_STORAGE_PROTOCOL)s",
    netapp_transport_type => "%(CONFIG_CINDER_NETAPP_TRANSPORT_TYPE)s",
    netapp_vfiler => "%(CONFIG_CINDER_NETAPP_VFILER)s",
    netapp_volume_list => ["%(CONFIG_CINDER_NETAPP_VOLUME_LIST)s"],
    netapp_vserver => "%(CONFIG_CINDER_NETAPP_VSERVER)s",
    expiry_thres_minutes => "%(CONFIG_CINDER_EXPIRY_THRES_MINUTES)s",  #d
    thres_avl_size_perc_start => "%(CONFIG_CINDER_THRES_AVL_SIZE_PERC_START)s",  #d
    thres_avl_size_perc_stop => "%(CONFIG_CINDER_THRES_AVL_SIZE_PERC_STOP)s",  #d
    nfs_shares_config => "%(CONFIG_CINDER_NFS_SHARES_CONFIG)s",
    netapp_copyoffload_tool_path => "%(CONFIG_CINDER_NETAPP_COPYOFFLOAD_TOOL_PATH)s",
    netapp_controller_ips => "%(CONFIG_CINDER_NETAPP_CONTROLLER_IPS)s",
    netapp_sa_password => "%(CONFIG_CINDER_NETAPP_SA_PASSWORD)s",
    netapp_storage_pools => "%(CONFIG_CINDER_NETAPP_STORAGE_POOLS)s",
    netapp_webservice_path => "%(CONFIG_CINDER_NETAPP_WEBSERVICE_PATH)s",

    #require => Package[$storage_package],
}