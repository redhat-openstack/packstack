class packstack::magnum ()
{
    create_resources(packstack::firewall, lookup('FIREWALL_MAGNUM_API_RULES', undef, undef, {}))

    class { 'magnum::db':
      database_connection => os_database_connection({
        'dialect'  => 'mysql+pymysql',
        'host'     => lookup('CONFIG_MARIADB_HOST_URL'),
        'username' => 'magnum',
        'password' => lookup('CONFIG_MAGNUM_DB_PW'),
        'database' => 'magnum',
      })
    }

    $magnum_host = lookup('CONFIG_KEYSTONE_HOST_URL')
    class { 'magnum::keystone::authtoken':
      www_authenticate_uri => lookup('CONFIG_KEYSTONE_PUBLIC_URL_VERSIONLESS'),
      auth_url             => lookup('CONFIG_KEYSTONE_ADMIN_URL'),
      password             => lookup('CONFIG_MAGNUM_KS_PW'),
    }

    class { 'magnum::keystone::keystone_auth':
      username            => 'magnum',
      password            => lookup('CONFIG_MAGNUM_KS_PW'),
      auth_url            => lookup('CONFIG_KEYSTONE_ADMIN_URL'),
      project_name        => 'services',
      user_domain_name    => 'Default',
      project_domain_name => 'Default',
    }

    $bind_host = lookup('CONFIG_IP_VERSION') ? {
      'ipv6'  => '::0',
      default => '0.0.0.0',
      # TO-DO(mmagr): Add IPv6 support when hostnames are used
    }

    class { 'magnum::api':
      service_name => 'httpd',
    }
    class { 'magnum::wsgi::apache':
      bind_host => $bind_host,
      workers   => lookup('CONFIG_SERVICE_WORKERS'),
    }

    class { 'magnum::conductor':
    }

    class { 'magnum::client':
    }

    class { 'magnum::clients':
      region_name => lookup('CONFIG_KEYSTONE_REGION')
    }

    class { 'magnum::certificates':
      cert_manager_type => 'local'
    }
}
