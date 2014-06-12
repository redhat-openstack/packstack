class { 'heat':
    keystone_host     => '%(CONFIG_CONTROLLER_HOST)s',
    keystone_password => '%(CONFIG_HEAT_KS_PW)s',
    auth_uri          => 'http://%(CONFIG_CONTROLLER_HOST)s:35357/v2.0',
    keystone_ec2_uri  => 'http://%(CONFIG_CONTROLLER_HOST)s:35357/v2.0',
    rpc_backend       => 'heat.openstack.common.rpc.impl_qpid',
    qpid_hostname     => '%(CONFIG_AMQP_HOST)s',
    qpid_username     => '%(CONFIG_AMQP_AUTH_USER)s',
    qpid_password     => '%(CONFIG_AMQP_AUTH_PASSWORD)s',
    verbose           => true,
    debug             => %(CONFIG_DEBUG_MODE)s,
    sql_connection    => "mysql://heat:%(CONFIG_HEAT_DB_PW)s@%(CONFIG_MYSQL_HOST)s/heat",
}
