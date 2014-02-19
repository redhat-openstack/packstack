
class { 'heat':
    keystone_host     => '%(CONFIG_KEYSTONE_HOST)s',
    keystone_password => '%(CONFIG_HEAT_KS_PW)s',
    auth_uri          => 'http://%(CONFIG_KEYSTONE_HOST)s:35357/v2.0',
    rpc_backend       => 'heat.openstack.common.rpc.impl_rabbit',
    rabbit_host       => '%(CONFIG_AMQP_HOST)s',
    rabbit_user  => '%(CONFIG_AMQP_AUTH_USER)s',
    rabbit_password   => '%(CONFIG_AMQP_AUTH_PASSWORD)s',
    verbose           => true,
    debug             => %(CONFIG_DEBUG_MODE)s,
}
