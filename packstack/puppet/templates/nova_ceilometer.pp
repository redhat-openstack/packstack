
class { 'ceilometer':
    metering_secret => '%(CONFIG_CEILOMETER_SECRET)s',
    qpid_hostname   => '%(CONFIG_QPID_HOST)s',
    qpid_username  => '%(CONFIG_QPID_AUTH_USER)s',
    qpid_password  => '%(CONFIG_QPID_AUTH_PASSWORD)s',
    rpc_backend     => 'ceilometer.openstack.common.rpc.impl_qpid',
    verbose         => true,
    debug           => %(CONFIG_DEBUG_MODE)s
}

class { 'ceilometer::agent::auth':
    auth_url      => 'http://%(CONFIG_KEYSTONE_HOST)s:35357/v2.0',
    auth_password => '%(CONFIG_CEILOMETER_KS_PW)s',
}

class { 'ceilometer::agent::compute':
}
