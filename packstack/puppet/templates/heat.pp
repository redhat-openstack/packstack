
class { 'heat':
    keystone_host     => '%(CONFIG_KEYSTONE_HOST)s',
    keystone_password => '%(CONFIG_HEAT_KS_PW)s',
    auth_uri          => 'http://%(CONFIG_KEYSTONE_HOST)s:35357/v2.0',
    rpc_backend       => 'heat.openstack.common.rpc.impl_qpid',
    qpid_hostname     => '%(CONFIG_QPID_HOST)s',
    qpid_username     => '%(CONFIG_QPID_AUTH_USER)s',
    qpid_password     => '%(CONFIG_QPID_AUTH_PASSWORD)s',
    verbose           => true,
    debug             => %(CONFIG_DEBUG_MODE)s,
    qpid_port         => '%(CONFIG_QPID_CLIENTS_PORT)s',
    qpid_protocol     => '%(CONFIG_QPID_PROTOCOL)s',
    sql_connection    => "mysql://heat:%(CONFIG_HEAT_DB_PW)s@%(CONFIG_MYSQL_HOST)s/heat",
}

class { 'heat::api':
}

class { 'heat::engine':
    heat_metadata_server_url      => 'http://%(CONFIG_HEAT_METADATA_HOST)s:8000',
    heat_waitcondition_server_url => 'http://%(CONFIG_HEAT_METADATA_HOST)s:8000/v1/waitcondition',
    heat_watch_server_url         => 'http://%(CONFIG_HEAT_WATCH_HOST)s:8003',
    auth_encryption_key           => '%(CONFIG_HEAT_AUTH_ENC_KEY)s',
}
