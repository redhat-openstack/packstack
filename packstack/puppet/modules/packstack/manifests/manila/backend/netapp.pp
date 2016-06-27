class packstack::manila::backend::netapp ()
{
    manila::backend::netapp{ 'netapp':
      driver_handles_share_servers         => hiera('CONFIG_MANILA_NETAPP_DRV_HANDLES_SHARE_SERVERS'),
      netapp_transport_type                => hiera('CONFIG_MANILA_NETAPP_TRANSPORT_TYPE'),
      netapp_login                         => hiera('CONFIG_MANILA_NETAPP_LOGIN'),
      netapp_password                      => hiera('CONFIG_MANILA_NETAPP_PASSWORD'),
      netapp_server_hostname               => hiera('CONFIG_MANILA_NETAPP_SERVER_HOSTNAME'),
      netapp_storage_family                => hiera('CONFIG_MANILA_NETAPP_STORAGE_FAMILY'),
      netapp_server_port                   => hiera('CONFIG_MANILA_NETAPP_SERVER_PORT'),
      netapp_vserver                       => hiera('CONFIG_MANILA_NETAPP_VSERVER', undef),
      netapp_aggregate_name_search_pattern => hiera('CONFIG_MANILA_NETAPP_AGGREGATE_NAME_SEARCH_PATTERN'),
      netapp_root_volume_aggregate         => hiera('CONFIG_MANILA_NETAPP_ROOT_VOLUME_AGGREGATE', undef),
      netapp_root_volume_name              => hiera('CONFIG_MANILA_NETAPP_ROOT_VOLUME_NAME', undef),
    }

    packstack::manila::network{ 'netapp': }
}
