class packstack::magnum ()
{
    create_resources(packstack::firewall, hiera('FIREWALL_MAGNUM_API_RULES', {}))

    $magnum_cfg_magnum_db_pw = hiera('CONFIG_MAGNUM_DB_PW')
    $magnum_cfg_magnum_mariadb_host = hiera('CONFIG_MARIADB_HOST_URL')
    class { '::magnum::db':
      database_connection => "mysql+pymysql://magnum:${magnum_cfg_magnum_db_pw}@${magnum_cfg_magnum_mariadb_host}/magnum",
    }

    $magnum_protocol = 'http'
    $magnum_host = hiera('CONFIG_KEYSTONE_HOST_URL')
    $magnum_port = '9511'
    $magnum_url = "${magnum_protocol}://${magnum_host}:$magnum_port/v1"
    class { '::magnum::keystone::authtoken':
      auth_uri                             => "${magnum_protocol}://${magnum_host}:5000/v3",
      auth_url                             => "${magnum_protocol}://${magnum_host}:35357",
      auth_version                         => 'v3',
      username                             => 'magnum',
      password                             => hiera('CONFIG_MAGNUM_KS_PW'),
      auth_type                            => 'password',
      memcached_servers                    => "${magnum_host}:11211",
      project_name                         => 'services'
    }

    class { '::magnum::api':
      enabled                              => true,
      host                                 => '0.0.0.0'
    }

    class { '::magnum::conductor':
    }

    class { '::magnum::client':
    }

    class { '::magnum::clients':
      region_name                          => hiera('CONFIG_KEYSTONE_REGION')
    }

    class { '::magnum::certificates':
      cert_manager_type => 'local'
    }
}
