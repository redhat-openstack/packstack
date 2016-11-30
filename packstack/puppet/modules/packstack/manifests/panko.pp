class packstack::panko ()
{
    create_resources(packstack::firewall, hiera('FIREWALL_PANKO_RULES', {}))

    $panko_cfg_db_pw = hiera('CONFIG_PANKO_DB_PW')
    $panko_cfg_mariadb_host = hiera('CONFIG_MARIADB_HOST_URL')

    class { '::panko::wsgi::apache':
      workers => hiera('CONFIG_SERVICE_WORKERS'),
      threads => hiera('CONFIG_SERVICE_WORKERS'),
      ssl     => false
    }

    include ::panko

    class { '::panko::db':
      database_connection => "mysql+pymysql://panko:${panko_cfg_db_pw}@${panko_cfg_mariadb_host}/panko?charset=utf8",
    }

    $bind_host = hiera('CONFIG_IP_VERSION') ? {
     'ipv6'  => '::0',
     default => '0.0.0.0',
    }

    class { '::panko::keystone::authtoken':
      auth_uri     => hiera('CONFIG_KEYSTONE_PUBLIC_URL'),
      auth_url     => hiera('CONFIG_KEYSTONE_ADMIN_URL'),
      auth_version => hiera('CONFIG_KEYSTONE_API_VERSION'),
      password     => hiera('CONFIG_PANKO_KS_PW')
    }

    class { '::panko::api':
      host         => $bind_host,
      service_name => 'httpd'
    }

    include ::panko::db::sync

}
