
package { 'curl': ensure => present }

class { 'memcached': }

class { 'swift::proxy':
  proxy_local_net_ip => hiera('CONFIG_CONTROLLER_HOST'),
  pipeline           => [
    'catch_errors',
    'bulk',
    'healthcheck',
    'cache',
    'crossdomain',
    'ratelimit',
    'authtoken',
    'keystone',
    'staticweb',
    'tempurl',
    'slo',
    'formpost',
    'account_quotas',
    'container_quotas',
    'proxy-server'
  ],
  account_autocreate => true,
}

# configure all of the middlewares
class { [
  'swift::proxy::catch_errors',
  'swift::proxy::healthcheck',
  'swift::proxy::cache',
  'swift::proxy::crossdomain',
  'swift::proxy::staticweb',
  'swift::proxy::tempurl',
  'swift::proxy::account_quotas',
  'swift::proxy::formpost',
  'swift::proxy::slo',
  'swift::proxy::container_quotas'
]: }

class { 'swift::proxy::bulk':
  max_containers_per_extraction => 10000,
  max_failed_extractions        => 1000,
  max_deletes_per_request       => 10000,
  yield_frequency               => 60,
}

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
  admin_password    => hiera('CONFIG_SWIFT_KS_PW'),
  # assume that the controller host is the swift api server
  auth_host         => hiera('CONFIG_CONTROLLER_HOST'),
}

