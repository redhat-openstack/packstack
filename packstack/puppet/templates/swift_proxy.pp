
package { 'curl': ensure => present }

class { 'memcached':
}

class { 'swift::proxy':
  proxy_local_net_ip => '%(CONFIG_SWIFT_PROXY)s',
  pipeline           => [
#    'catch_errors',
    'healthcheck',
    'cache',
#    'ratelimit',
    'authtoken',
    'keystone',
    'proxy-server'
  ],
  account_autocreate => true,
}

# configure all of the middlewares
class { [
    'swift::proxy::catch_errors',
    'swift::proxy::healthcheck',
    'swift::proxy::cache',
]: }

class { 'swift::proxy::ratelimit':
    clock_accuracy         => 1000,
    max_sleep_time_seconds => 60,
    log_sleep_time_seconds => 0,
    rate_buffer_seconds    => 5,
    account_ratelimit      => 0
}

class { 'swift::proxy::keystone':
    operator_roles => ['admin', 'SwiftOperator'],
}

class { 'swift::proxy::authtoken':
    admin_user        => 'swift',
    admin_tenant_name => 'services',
    admin_password    => '%(CONFIG_SWIFT_KS_PW)s',
    # assume that the controller host is the swift api server
    auth_host         => '%(CONFIG_KEYSTONE_HOST)s',
}

firewall { '001 swift proxy incoming':
    proto    => 'tcp',
    dport    => ['8080'],
    action   => 'accept',
}
