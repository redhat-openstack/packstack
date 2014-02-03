
# Ensure Firewall changes happen before nova services start
# preventing a clash with rules being set by nova-compute and nova-network
Firewall <| |> -> Class['nova']

nova_config{
    "DEFAULT/sql_connection": value => "%(CONFIG_NOVA_SQL_CONN)s";
    "DEFAULT/metadata_host": value => "%(CONFIG_NOVA_METADATA_HOST)s";
}

class { "nova":
    glance_api_servers => "%(CONFIG_GLANCE_HOST)s:9292",
    qpid_hostname      => "%(CONFIG_QPID_HOST)s",
    qpid_username      => '%(CONFIG_QPID_AUTH_USER)s',
    qpid_password      => '%(CONFIG_QPID_AUTH_PASSWORD)s',
    rpc_backend        => 'nova.openstack.common.rpc.impl_qpid',
    qpid_port          => '%(CONFIG_QPID_CLIENTS_PORT)s',
    qpid_protocol      => '%(CONFIG_QPID_PROTOCOL)s',
    verbose            => true,
    debug              => %(CONFIG_DEBUG_MODE)s,
}
