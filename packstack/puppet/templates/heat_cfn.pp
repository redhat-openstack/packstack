
class { 'heat':
    keystone_host     => '%(CONFIG_KEYSTONE_HOST)s',
    keystone_password => '%(CONFIG_HEAT_KS_PW)s',
    auth_uri          => 'http://%(CONFIG_KEYSTONE_HOST)s:35357/v2.0',
    rpc_backend   => 'heat.openstack.common.rpc.impl_qpid',
    qpid_hostname => '%(CONFIG_QPID_HOST)s',
    verbose       => true,
    debug         => false
}

class {"heat::db":
    sql_connection => "mysql://heat:%(CONFIG_HEAT_DB_PW)s@%(CONFIG_MYSQL_HOST)s/heat"
}

class { 'heat::api_cfn':
}

