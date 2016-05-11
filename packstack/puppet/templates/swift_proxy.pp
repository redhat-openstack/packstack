
package { 'curl': ensure => present }

$bind_host = hiera('CONFIG_IP_VERSION') ? {
  'ipv6'  => '::0',
  default => '0.0.0.0',
  # TO-DO(mmagr): Add IPv6 support when hostnames are used
}

# hack for memcached, for now we bind to localhost on ipv6
# https://bugzilla.redhat.com/show_bug.cgi?id=1210658
$memcached_bind_host = hiera('CONFIG_IP_VERSION') ? {
  'ipv6'  => 'localhost6',
  default => '0.0.0.0',
  # TO-DO(mmagr): Add IPv6 support when hostnames are used
}

class { '::memcached':
  listen_ip  => $memcached_bind_host,
  max_memory => '10%%',
}

class { '::swift::proxy':
  # swift seems to require ipv6 address without brackets
  proxy_local_net_ip => hiera('CONFIG_STORAGE_HOST'),
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
    'proxy-server',
  ],
  account_autocreate => true,
  workers => $service_workers
}

# configure all of the middlewares
class { [
  '::swift::proxy::catch_errors',
  '::swift::proxy::healthcheck',
  '::swift::proxy::cache',
  '::swift::proxy::crossdomain',
  '::swift::proxy::staticweb',
  '::swift::proxy::tempurl',
  '::swift::proxy::account_quotas',
  '::swift::proxy::formpost',
  '::swift::proxy::slo',
  '::swift::proxy::container_quotas',
]: }

class { '::swift::proxy::bulk':
  max_containers_per_extraction => 10000,
  max_failed_extractions        => 1000,
  max_deletes_per_request       => 10000,
  yield_frequency               => 60,
}

class { '::swift::proxy::ratelimit':
  clock_accuracy         => 1000,
  max_sleep_time_seconds => 60,
  log_sleep_time_seconds => 0,
  rate_buffer_seconds    => 5,
  account_ratelimit      => 0,
}

class { '::swift::proxy::keystone':
  operator_roles => ['admin', 'SwiftOperator', '_member_'],
}

class { '::swift::proxy::authtoken':
  admin_user        => 'swift',
  admin_tenant_name => 'services',
  admin_password    => hiera('CONFIG_SWIFT_KS_PW'),
  # assume that the controller host is the swift api server
  auth_uri          => hiera('CONFIG_KEYSTONE_PUBLIC_URL'),
  identity_uri      => hiera('CONFIG_KEYSTONE_ADMIN_URL'),
}

class { '::swift::objectexpirer': }
