
class { 'ceilometer':
    metering_secret => '%(CONFIG_CEILOMETER_SECRET)s',
    qpid_hostname   => '%(CONFIG_QPID_HOST)s',
    rpc_backend     => 'ceilometer.openstack.common.rpc.impl_qpid',
    verbose         => true,
    debug           => true,
}

class { 'ceilometer::agent::compute':
    auth_url      => 'http://%(CONFIG_KEYSTONE_HOST)s:35357/v2.0',
    auth_password => '%(CONFIG_CEILOMETER_KS_PW)s',
}

# if fqdn is not set correctly we have to tell compute agent which host it should query
if !$::fqdn or $::fqdn != $::hostname {
    ceilometer_config {
        'DEFAULT/host': value => $::hostname
    }
}
