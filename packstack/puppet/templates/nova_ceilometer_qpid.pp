
class { 'ceilometer':
    metering_secret => '%(CONFIG_CEILOMETER_SECRET)s',
    qpid_hostname   => '%(CONFIG_AMQP_HOST)s',
    qpid_username  => '%(CONFIG_AMQP_AUTH_USER)s',
    qpid_password  => '%(CONFIG_AMQP_AUTH_PASSWORD)s',
    rpc_backend     => 'ceilometer.openstack.common.rpc.impl_qpid',
    verbose         => true,
    debug           => %(CONFIG_DEBUG_MODE)s
}

