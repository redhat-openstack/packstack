
manila::backend::netapp{ 'netapp':
  netapp_nas_transport_type            => hiera('CONFIG_MANILA_NETAPP_NAS_TRANSPORT_TYPE'),
  netapp_nas_login                     => hiera('CONFIG_MANILA_NETAPP_NAS_LOGIN'),
  netapp_nas_password                  => hiera('CONFIG_MANILA_NETAPP_NAS_PASSWORD'),
  netapp_nas_server_hostname           => hiera('CONFIG_MANILA_NETAPP_NAS_SERVER_HOSTNAME'),
  netapp_aggregate_name_search_pattern => hiera('CONFIG_MANILA_NETAPP_AGGREGATE_NAME_SEARCH_PATTERN'),
  netapp_root_volume_aggregate         => hiera('CONFIG_MANILA_NETAPP_ROOT_VOLUME_AGGREGATE'),
  netapp_root_volume_name              => hiera('CONFIG_MANILA_NETAPP_ROOT_VOLUME_NAME'),
}

packstack::manila::network{ 'netapp': }
