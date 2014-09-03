# Copyright (c) – 2014, Ryan Hefner.  All rights reserved.

package { 'nfs-utils': ensure => present }

cinder::backend::netapp { 'netapp':
  netapp_login              => "%(CONFIG_CINDER_NETAPP_LOGIN)s",
  netapp_password           => "%(CONFIG_CINDER_NETAPP_PASSWORD)s",
  netapp_server_hostname    => "%(CONFIG_CINDER_NETAPP_HOSTNAME)s",
  netapp_server_port        => "%(CONFIG_CINDER_NETAPP_SERVER_PORT)s",
  netapp_storage_family     => "%(CONFIG_CINDER_NETAPP_STORAGE_FAMILY)s",
  netapp_storage_protocol   => "%(CONFIG_CINDER_NETAPP_STORAGE_PROTOCOL)s",
  netapp_transport_type     => "%(CONFIG_CINDER_NETAPP_TRANSPORT_TYPE)s",
  netapp_vserver            => "%(CONFIG_CINDER_NETAPP_VSERVER)s",
  expiry_thres_minutes      => "%(CONFIG_CINDER_NETAPP_EXPIRY_THRES_MINUTES)s",
  thres_avl_size_perc_start => "%(CONFIG_CINDER_NETAPP_THRES_AVL_SIZE_PERC_START)s",
  thres_avl_size_perc_stop  => "%(CONFIG_CINDER_NETAPP_THRES_AVL_SIZE_PERC_STOP)s",
  nfs_shares_config         => "%(CONFIG_CINDER_NETAPP_NFS_SHARES_CONFIG)s",
  require                   => Package['nfs-utils'],
}

cinder::type { 'cinder_netapp_cdot_nfs':
  set_key   => 'volume_backend_name',
  set_value => 'netapp',
  require   => Class['cinder::api'],
}
