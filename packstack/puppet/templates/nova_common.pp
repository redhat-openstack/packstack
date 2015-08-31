
# Ensure Firewall changes happen before nova services start
# preventing a clash with rules being set by nova-compute and nova-network
Firewall <| |> -> Class['nova']

nova_config{
    "DEFAULT/default_floating_pool": value => '%(CONFIG_NOVA_NETWORK_DEFAULTFLOATINGPOOL)s';
    "DEFAULT/sql_connection": value => "%(CONFIG_NOVA_SQL_CONN)s";
    "DEFAULT/metadata_host": value => "%(CONFIG_CONTROLLER_HOST)s";
}
