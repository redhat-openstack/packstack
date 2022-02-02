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

    $default_store = hiera('CONFIG_GLANCE_BACKEND') ? {
      'swift' => 'swift',
      default => 'file',
    }

    class { 'glance::api::authtoken':
      www_authenticate_uri => hiera('CONFIG_KEYSTONE_PUBLIC_URL'),
      auth_url             => hiera('CONFIG_KEYSTONE_ADMIN_URL'),
      password             => hiera('CONFIG_GLANCE_KS_PW'),
    }

    class { 'glance::api::logging':
      debug => hiera('CONFIG_DEBUG_MODE'),
    }

    class { 'glance::api::db':
      database_connection => "mysql+pymysql://glance:${glance_ks_pw}@${glance_mariadb_host}/glance",
    }

    class { 'glance::api':
      bind_host           => $bind_host,
      pipeline            => 'keystone',
      workers             => hiera('CONFIG_SERVICE_WORKERS'),
      enabled_backends    => ["${default_store}:${default_store}", "http:http"],
      default_backend     => $default_store,
    }

    glance::backend::multistore::http { 'http': }
}
