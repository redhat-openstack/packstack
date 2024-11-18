class packstack::heat ()
{
    create_resources(packstack::firewall, lookup('FIREWALL_HEAT_RULES', undef, undef, {}))

    $bind_host = lookup('CONFIG_IP_VERSION') ? {
      'ipv6'  => '::0',
      default => '0.0.0.0',
    }

    class { 'heat::api':
      service_name => 'httpd',
    }
    class { 'heat::wsgi::apache_api':
      bind_host => $bind_host,
      workers   => lookup('CONFIG_SERVICE_WORKERS'),
    }

    $memcache_servers = lookup('CONFIG_IP_VERSION') ? {
      'ipv6'  => ['[::1]:11211'],
      default => ['127.0.0.1:11211'],
    }
    class {'heat::cache':
      enabled          => true,
      backend          => 'dogpile.cache.pymemcache',
      memcache_servers => $memcache_servers,
    }
    include packstack::memcached
    Class['memcached'] -> Anchor['heat::service::begin']

    $heat_cfg_ctrl_host = lookup('CONFIG_KEYSTONE_HOST_URL')

    class { 'heat::engine':
      heat_metadata_server_url      => "http://${heat_cfg_ctrl_host}:8000",
      heat_waitcondition_server_url => "http://${heat_cfg_ctrl_host}:8000/v1/waitcondition",
      auth_encryption_key           => lookup('CONFIG_HEAT_AUTH_ENC_KEY'),
      num_engine_workers            => lookup('CONFIG_SERVICE_WORKERS'),
    }

    class { 'heat::keystone::domain':
      domain_name     => lookup('CONFIG_HEAT_DOMAIN'),
      domain_admin    => lookup('CONFIG_HEAT_DOMAIN_ADMIN'),
      domain_password => lookup('CONFIG_HEAT_DOMAIN_PASSWORD'),
    }
}
