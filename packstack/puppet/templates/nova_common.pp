
# Ensure Firewall changes happen before nova services start
# preventing a clash with rules being set by nova-compute and nova-network
Firewall <| |> -> Class['nova']

nova_config{
    "DEFAULT/metadata_host": value => "%(CONFIG_NOVA_API_HOST)s";
    "DEFAULT/sql_connection": value => "%(CONFIG_NOVA_SQL_CONN)s";
}

class {"nova":
    glance_api_servers => "%(CONFIG_GLANCE_HOST)s:9292",
    qpid_hostname => "%(CONFIG_QPID_HOST)s",
    rpc_backend => 'nova.openstack.common.rpc.impl_qpid',
    verbose     => 'True',
}
