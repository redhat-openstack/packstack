class packstack::magnum ()
{
    create_resources(packstack::firewall, lookup('FIREWALL_MAGNUM_API_RULES', undef, undef, {}))

    $magnum_cfg_magnum_db_pw = lookup('CONFIG_MAGNUM_DB_PW')
    $magnum_cfg_magnum_mariadb_host = lookup('CONFIG_MARIADB_HOST_URL')
    class { 'magnum::db':
      database_connection => "mysql+pymysql://magnum:${magnum_cfg_magnum_db_pw}@${magnum_cfg_magnum_mariadb_host}/magnum",
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

    class { 'magnum::api':
      enabled => true,
      host    => '0.0.0.0'
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
