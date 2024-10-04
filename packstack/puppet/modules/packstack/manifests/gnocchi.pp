class packstack::gnocchi ()
{
    create_resources(packstack::firewall, lookup('FIREWALL_GNOCCHI_RULES', undef, undef, {}))

    $config_gnocchi_coordination_backend = lookup('CONFIG_CEILOMETER_COORDINATION_BACKEND')

    if $config_gnocchi_coordination_backend == 'redis' {
      $redis_host = hiera('CONFIG_REDIS_HOST_URL')
      $redis_port = hiera('CONFIG_REDIS_PORT')
      $coordination_url = "redis://${redis_host}:${redis_port}"
      Service<| title == 'redis' |> -> Anchor['gnocchi::service::begin']
    } else {
      $coordination_url = ''
    }

    $gnocchi_cfg_db_pw = lookup('CONFIG_GNOCCHI_DB_PW')
    $gnocchi_cfg_mariadb_host = lookup('CONFIG_MARIADB_HOST_URL')

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
      database_connection => "mysql+pymysql://gnocchi:${gnocchi_cfg_db_pw}@${gnocchi_cfg_mariadb_host}/gnocchi?charset=utf8",
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
      flush_delay         => '10',
    }

    include gnocchi::client
}
