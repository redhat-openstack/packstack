class packstack::placement ()
{
    $placement_db_pw = lookup('CONFIG_NOVA_DB_PW')
    $placement_mariadb_host = lookup('CONFIG_MARIADB_HOST_URL')
    $bind_host = lookup('CONFIG_IP_VERSION') ? {
      'ipv6'  => '::0',
      default => '0.0.0.0',
      # TO-DO(mmagr): Add IPv6 support when hostnames are used
    }

    include packstack::keystone::placement
    include placement

    class { 'placement::logging':
      debug => lookup('CONFIG_DEBUG_MODE'),
    }

    class { 'placement::db':
      database_connection => "mysql+pymysql://placement:${placement_db_pw}@${placement_mariadb_host}/placement",
    }

    include placement::db::sync
    include placement::api

    class { 'placement::wsgi::apache':
      bind_host => $bind_host,
      ssl       => false,
      workers   => lookup('CONFIG_SERVICE_WORKERS'),
    }
}
