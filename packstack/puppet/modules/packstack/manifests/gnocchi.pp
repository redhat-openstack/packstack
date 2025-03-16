class packstack::gnocchi ()
{
    create_resources(packstack::firewall, lookup('FIREWALL_GNOCCHI_RULES', undef, undef, {}))

    $config_gnocchi_coordination_backend = lookup('CONFIG_CEILOMETER_COORDINATION_BACKEND')

    if $config_gnocchi_coordination_backend == 'redis' {
      $coordination_url = os_url({
        'scheme' => 'redis',
        'host'   => lookup('CONFIG_REDIS_HOST_URL'),
        'port'   => lookup('CONFIG_REDIS_PORT'),
      })
      Service<| title == 'redis' |> -> Anchor['gnocchi::service::begin']
    } else {
      $coordination_url = uhdef
    }

    class { 'gnocchi::wsgi::apache':
      workers => lookup('CONFIG_SERVICE_WORKERS'),
      ssl     => false
    }

    class { 'gnocchi':
      coordination_url => $coordination_url,
    }

    class { 'gnocchi::keystone::authtoken':
      www_authenticate_uri => lookup('CONFIG_KEYSTONE_PUBLIC_URL'),
      auth_url             => lookup('CONFIG_KEYSTONE_ADMIN_URL'),
      password             => lookup('CONFIG_GNOCCHI_KS_PW')
    }

    class { 'gnocchi::db':
      database_connection => os_database_connection({
        'dialect'  => 'mysql+pymysql',
        'host'     => lookup('CONFIG_MARIADB_HOST_URL'),
        'username' => 'gnocchi',
        'password' => lookup('CONFIG_GNOCCHI_DB_PW'),
        'database' => 'gnocchi',
        'charset'  => 'utf8',
      })
    }

    class { 'gnocchi::api':
      service_name => 'httpd',
      sync_db      => true,
    }

    class { 'gnocchi::storage': }
    class { 'gnocchi::storage::file': }

    class { 'gnocchi::metricd': }

    class { 'gnocchi::statsd':
      resource_id         => '5e3fcbe2-7aab-475d-b42c-a440aa42e5ad',
      archive_policy_name => 'high',
    }

    include gnocchi::client
}
