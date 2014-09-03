# Copyright (c) – 2014, Ryan Hefner.  All rights reserved.

package { 'iscsi-initiator-utils': ensure => present }

cinder_config {
  "DEFAULT/enabled_backends": value => "myBackend";
}

cinder::backend::netapp{ 'myBackend':
  netapp_login            => "%(CONFIG_CINDER_NETAPP_LOGIN)s",
  netapp_password         => "%(CONFIG_CINDER_NETAPP_PASSWORD)s",
  netapp_server_hostname  => "%(CONFIG_CINDER_NETAPP_HOSTNAME)s",
  netapp_server_port      => "%(CONFIG_CINDER_NETAPP_SERVER_PORT)s",
  netapp_size_multiplier  => "%(CONFIG_CINDER_NETAPP_SIZE_MULTIPLIER)s",
  netapp_storage_family   => "%(CONFIG_CINDER_NETAPP_STORAGE_FAMILY)s",
  netapp_storage_protocol => "%(CONFIG_CINDER_NETAPP_STORAGE_PROTOCOL)s",
  netapp_transport_type   => "%(CONFIG_CINDER_NETAPP_TRANSPORT_TYPE)s",
  netapp_vfiler           => "%(CONFIG_CINDER_NETAPP_VFILER)s",
  netapp_volume_list      => ["%(CONFIG_CINDER_NETAPP_VOLUME_LIST)s"],

  require => Package['iscsi-initiator-utils'],
}
