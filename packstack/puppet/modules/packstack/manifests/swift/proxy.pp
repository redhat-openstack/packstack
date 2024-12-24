class packstack::swift::proxy ()
{
    create_resources(packstack::firewall, lookup('FIREWALL_SWIFT_PROXY_RULES', undef, undef, {}))
    ensure_packages(['curl'], {'ensure' => 'present'})

    $bind_host = lookup('CONFIG_IP_VERSION') ? {
      'ipv6'  => '::0',
      default => '0.0.0.0',
      # TO-DO(mmagr): Add IPv6 support when hostnames are used
    }

    include packstack::memcached

    if lookup('CONFIG_CEILOMETER_INSTALL') == 'y' and
      lookup('CONFIG_ENABLE_CEILOMETER_MIDDLEWARE') == 'y' {
      $swift_pipeline = [
        'catch_errors',
        'gatekeeper',
        'healthcheck',
        'proxy-logging',
        'cache',
        'listing_formats',
        'bulk',
        'tempurl',
        'ratelimit',
        'crossdomain',
        'authtoken',
        'keystone',
        'formpost',
        'staticweb',
        'copy',
        'container_quotas',
        'account_quotas',
        'slo',
        'dlo',
        'ceilometer',
        'proxy-logging',
        'proxy-server',
      ]
    } else {
      $swift_pipeline = [
        'catch_errors',
        'gatekeeper',
        'healthcheck',
        'proxy-logging',
        'cache',
        'listing_formats',
        'bulk',
        'tempurl',
        'ratelimit',
        'crossdomain',
        'authtoken',
        'keystone',
        'formpost',
        'staticweb',
        'copy',
        'container_quotas',
        'account_quotas',
        'slo',
        'dlo',
        'proxy-logging',
        'proxy-server',
      ]
    }

    class { 'swift::proxy':
      # swift seems to require ipv6 address without brackets
      proxy_local_net_ip => lookup('CONFIG_STORAGE_HOST'),
      pipeline           => $swift_pipeline,
      account_autocreate => true,
      workers            => lookup('CONFIG_SERVICE_WORKERS'),
    }

    # configure all of the middlewares
    class { [
      'swift::proxy::catch_errors',
      'swift::proxy::gatekeeper',
      'swift::proxy::healthcheck',
      'swift::proxy::proxy_logging',
      'swift::proxy::listing_formats',
      'swift::proxy::bulk',
      'swift::proxy::tempurl',
      'swift::proxy::ratelimit',
      'swift::proxy::crossdomain',
      'swift::proxy::formpost',
      'swift::proxy::staticweb',
      'swift::proxy::copy',
      'swift::proxy::container_quotas',
      'swift::proxy::account_quotas',
      'swift::proxy::slo',
      'swift::proxy::dlo',
    ]: }

    $memcache_servers = lookup('CONFIG_IP_VERSION') ? {
      'ipv6'  => ['[::1]:11211'],
      default => ['127.0.0.1:11211'],
    }
    class {'swift::proxy::cache':
      memcache_servers => $memcache_servers,
    }

    class { 'swift::proxy::keystone':
      operator_roles => ['admin', 'SwiftOperator', 'member'],
    }

    class { 'swift::proxy::authtoken':
      password             => lookup('CONFIG_SWIFT_KS_PW'),
      # assume that the controller host is the swift api server
      www_authenticate_uri => lookup('CONFIG_KEYSTONE_PUBLIC_URL_VERSIONLESS'),
      auth_url             => lookup('CONFIG_KEYSTONE_ADMIN_URL'),
    }

    class { 'swift::proxy::versioned_writes':
      allow_versioned_writes => true,
    }

    class { 'swift::objectexpirer':
      memcache_servers => $memcache_servers,
    }
}
