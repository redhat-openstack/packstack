class { 'ceilometer::db':
    database_connection => 'mongodb://%(CONFIG_MONGODB_HOST)s:27017/ceilometer',
}

class { 'ceilometer::collector':
}

class { 'ceilometer::agent::auth':
    auth_url      => 'http://%(CONFIG_CONTROLLER_HOST)s:35357/v2.0',
    auth_password => '%(CONFIG_CEILOMETER_KS_PW)s',
}

class { 'ceilometer::agent::central':
}

class { 'ceilometer::alarm::notifier':
}

class { 'ceilometer::alarm::evaluator':
}

class { 'ceilometer::api':
    keystone_host     => '%(CONFIG_CONTROLLER_HOST)s',
    keystone_password => '%(CONFIG_CEILOMETER_KS_PW)s',
}
