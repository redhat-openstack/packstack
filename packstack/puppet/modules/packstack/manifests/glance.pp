class packstack::glance ()
{
    create_resources(packstack::firewall, hiera('FIREWALL_GLANCE_RULES', {}))

    $glance_ks_pw = hiera('CONFIG_GLANCE_DB_PW')
    $glance_mariadb_host = hiera('CONFIG_MARIADB_HOST_URL')
    $glance_cfg_ctrl_host = hiera('CONFIG_KEYSTONE_HOST_URL')

    # glance option bind_host requires address without brackets
    $bind_host = hiera('CONFIG_IP_VERSION') ? {
      'ipv6'  => '::0',
      default => '0.0.0.0',
      # TO-DO(mmagr): Add IPv6 support when hostnames are used
    }
    # magical hack for magical config - glance option registry_host requires brackets
    $registry_host = hiera('CONFIG_IP_VERSION') ? {
      'ipv6'  => '[::0]',
      default => '0.0.0.0',
      # TO-DO(mmagr): Add IPv6 support when hostnames are used
    }
    $default_store = hiera('CONFIG_GLANCE_BACKEND') ? {
      'swift' => 'swift',
      default => 'file',
    }

    class { '::glance::api::authtoken':
      auth_uri => hiera('CONFIG_KEYSTONE_PUBLIC_URL'),
      auth_url => hiera('CONFIG_KEYSTONE_ADMIN_URL'),
      password => hiera('CONFIG_GLANCE_KS_PW'),
    }

    class { '::glance::api':
      bind_host           => $bind_host,
      registry_host       => $registry_host,
      pipeline            => 'keystone',
      database_connection => "mysql+pymysql://glance:${glance_ks_pw}@${glance_mariadb_host}/glance",
      debug               => hiera('CONFIG_DEBUG_MODE'),
      os_region_name      => hiera('CONFIG_KEYSTONE_REGION'),
      workers             => hiera('CONFIG_SERVICE_WORKERS'),
      stores              => ['file', 'http', 'swift'],
      default_store       => $default_store,
    }

    class { '::glance::registry::authtoken':
      auth_uri => hiera('CONFIG_KEYSTONE_PUBLIC_URL'),
      auth_url => hiera('CONFIG_KEYSTONE_ADMIN_URL'),
      password => hiera('CONFIG_GLANCE_KS_PW'),
    }

    class { '::glance::registry':
      bind_host           => $bind_host,
      database_connection => "mysql+pymysql://glance:${glance_ks_pw}@${glance_mariadb_host}/glance",
      debug               => hiera('CONFIG_DEBUG_MODE'),
      workers             => hiera('CONFIG_SERVICE_WORKERS'),
    }
}
