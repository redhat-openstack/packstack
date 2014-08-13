$config_use_neutron = hiera('CONFIG_NEUTRON_INSTALL')

if $config_use_neutron == 'y' {
    $default_floating_pool = 'public'
} else {
    $default_floating_pool = 'nova'
}

# Ensure Firewall changes happen before nova services start
# preventing a clash with rules being set by nova-compute and nova-network
Firewall <| |> -> Class['nova']

nova_config{
  'DEFAULT/sql_connection': value => hiera('CONFIG_NOVA_SQL_CONN_NOPW');
  'DEFAULT/metadata_host':  value => hiera('CONFIG_CONTROLLER_HOST');
  'DEFAULT/default_floating_pool': value => $default_floating_pool;
}
