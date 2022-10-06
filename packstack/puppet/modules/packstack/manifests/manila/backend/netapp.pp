class packstack::manila::backend::netapp ()
{
    manila::backend::netapp{ 'netapp':
      driver_handles_share_servers         => lookup('CONFIG_MANILA_NETAPP_DRV_HANDLES_SHARE_SERVERS'),
      netapp_transport_type                => lookup('CONFIG_MANILA_NETAPP_TRANSPORT_TYPE'),
      netapp_login                         => lookup('CONFIG_MANILA_NETAPP_LOGIN'),
      netapp_password                      => lookup('CONFIG_MANILA_NETAPP_PASSWORD'),
      netapp_server_hostname               => lookup('CONFIG_MANILA_NETAPP_SERVER_HOSTNAME'),
      netapp_storage_family                => lookup('CONFIG_MANILA_NETAPP_STORAGE_FAMILY'),
      netapp_server_port                   => lookup('CONFIG_MANILA_NETAPP_SERVER_PORT'),
      netapp_vserver                       => lookup('CONFIG_MANILA_NETAPP_VSERVER', undef, undef, undef),
      netapp_aggregate_name_search_pattern => lookup('CONFIG_MANILA_NETAPP_AGGREGATE_NAME_SEARCH_PATTERN'),
      netapp_root_volume_aggregate         => lookup('CONFIG_MANILA_NETAPP_ROOT_VOLUME_AGGREGATE', undef, undef, undef),
      netapp_root_volume_name              => lookup('CONFIG_MANILA_NETAPP_ROOT_VOLUME_NAME', undef, undef, undef),
    }

    packstack::manila::network{ 'netapp': }
}
