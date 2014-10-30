# Copyright (c) – 2014, Ryan Hefner.  All rights reserved.

package { 'iscsi-initiator-utils': ensure => present }

cinder::backend::netapp { 'netapp':
  netapp_login            => hiera('CONFIG_CINDER_NETAPP_LOGIN'),
  netapp_password         => hiera('CONFIG_CINDER_NETAPP_PASSWORD'),
  netapp_server_hostname  => hiera('CONFIG_CINDER_NETAPP_HOSTNAME'),
  netapp_server_port      => hiera('CONFIG_CINDER_NETAPP_SERVER_PORT'),
  netapp_size_multiplier  => hiera('CONFIG_CINDER_NETAPP_SIZE_MULTIPLIER'),
  netapp_storage_family   => hiera('CONFIG_CINDER_NETAPP_STORAGE_FAMILY'),
  netapp_storage_protocol => hiera('CONFIG_CINDER_NETAPP_STORAGE_PROTOCOL'),
  netapp_transport_type   => hiera('CONFIG_CINDER_NETAPP_TRANSPORT_TYPE'),
  netapp_vserver          => hiera('CONFIG_CINDER_NETAPP_VSERVER'),
  require                 => Package['iscsi-initiator-utils'],
}

cinder::type { 'cinder_netapp_cdot_iscsi':
  set_key   => 'volume_backend_name',
  set_value => 'netapp',
  require   => Class['cinder::api'],
}
