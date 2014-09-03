# Copyright (c) – 2014, Ryan Hefner.  All rights reserved.

package { 'nfs-utils': ensure => present }

cinder_config {
  "DEFAULT/enabled_backends": value => "myBackend";
}

cinder::backend::netapp{ 'myBackend':
  netapp_login              => "%(CONFIG_CINDER_NETAPP_LOGIN)s",
  netapp_password           => "%(CONFIG_CINDER_NETAPP_PASSWORD)s",
  netapp_server_hostname    => "%(CONFIG_CINDER_NETAPP_HOSTNAME)s",
  netapp_server_port        => "%(CONFIG_CINDER_NETAPP_SERVER_PORT)s",
  netapp_storage_family     => "%(CONFIG_CINDER_NETAPP_STORAGE_FAMILY)s",
  netapp_storage_protocol   => "%(CONFIG_CINDER_NETAPP_STORAGE_PROTOCOL)s",
  netapp_transport_type     => "%(CONFIG_CINDER_NETAPP_TRANSPORT_TYPE)s",
  expiry_thres_minutes      => "%(CONFIG_CINDER_EXPIRY_THRES_MINUTES)s",
  thres_avl_size_perc_start => "%(CONFIG_CINDER_NETAPP_THRES_AVL_SIZE_PERC_START)s",
  thres_avl_size_perc_stop  => "%(CONFIG_CINDER_NETAPP_THRES_AVL_SIZE_PERC_STOP)s",
  nfs_shares_config         => "%(CONFIG_CINDER_NETAPP_NFS_SHARES_CONFIG)s",

  require => Package['nfs-utils'],
}
