
class { 'ceilometer::keystone::auth':
    password => '%(CONFIG_CEILOMETER_KS_PW)s',
    public_address => "%(CONFIG_CEILOMETER_HOST)s",
    admin_address => "%(CONFIG_CEILOMETER_HOST)s",
    internal_address => "%(CONFIG_CEILOMETER_HOST)s",
}
