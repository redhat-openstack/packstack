# Copyright (c) – 2014, Ryan Hefner.  All rights reserved.

package { 'nfs-utils': ensure => present }

cinder::backend::netapp { 'netapp':
  netapp_login              => hiera('CONFIG_CINDER_NETAPP_LOGIN'),
  netapp_password           => hiera('CONFIG_CINDER_NETAPP_PASSWORD'),
  netapp_server_hostname    => hiera('CONFIG_CINDER_NETAPP_HOSTNAME'),
  netapp_server_port        => hiera('CONFIG_CINDER_NETAPP_SERVER_PORT'),
  netapp_storage_family     => hiera('CONFIG_CINDER_NETAPP_STORAGE_FAMILY'),
  netapp_storage_protocol   => hiera('CONFIG_CINDER_NETAPP_STORAGE_PROTOCOL'),
  netapp_transport_type     => hiera('CONFIG_CINDER_NETAPP_TRANSPORT_TYPE'),
  netapp_vserver            => hiera('CONFIG_CINDER_NETAPP_VSERVER'),
  expiry_thres_minutes      => hiera('CONFIG_CINDER_NETAPP_EXPIRY_THRES_MINUTES'),
  thres_avl_size_perc_start => hiera('CONFIG_CINDER_NETAPP_THRES_AVL_SIZE_PERC_START'),
  thres_avl_size_perc_stop  => hiera('CONFIG_CINDER_NETAPP_THRES_AVL_SIZE_PERC_STOP'),
  nfs_shares_config         => hiera('CONFIG_CINDER_NETAPP_NFS_SHARES_CONFIG'),
  require                   => Package['nfs-utils'],
}

cinder::type { 'cinder_netapp_cdot_nfs':
  set_key   => 'volume_backend_name',
  set_value => 'netapp',
  require   => Class['cinder::api'],
}
