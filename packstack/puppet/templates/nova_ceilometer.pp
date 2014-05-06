
class { 'ceilometer::agent::auth':
    auth_url      => 'http://%(CONFIG_CONTROLLER_HOST)s:35357/v2.0',
    auth_password => '%(CONFIG_CEILOMETER_KS_PW)s',
}

class { 'ceilometer::agent::compute':
}
