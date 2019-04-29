class packstack::placement ()
{
    $placement_db_pw = hiera('CONFIG_NOVA_DB_PW')
    $placement_mariadb_host = hiera('CONFIG_MARIADB_HOST_URL')
    $bind_host = hiera('CONFIG_IP_VERSION') ? {
      'ipv6'  => '::0',
      default => '0.0.0.0',
      # TO-DO(mmagr): Add IPv6 support when hostnames are used
    }

    include ::packstack::keystone::placement
    include ::placement

    class { '::placement::logging':
      debug => hiera('CONFIG_DEBUG_MODE'),
    }

    class { '::placement::db':
      database_connection => "mysql+pymysql://placement:${placement_db_pw}@${placement_mariadb_host}/placement",
    }

    include ::placement::db::sync

    class { '::placement::wsgi::apache':
      bind_host => $bind_host,
      api_port  => '8778',
      ssl       => false,
      workers   => hiera('CONFIG_SERVICE_WORKERS'),
    }
}
