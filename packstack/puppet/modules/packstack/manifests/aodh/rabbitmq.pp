class packstack::aodh::rabbitmq ()
{
    $kombu_ssl_ca_certs = lookup('CONFIG_AMQP_SSL_CACERT_FILE', undef, undef, undef)
    $kombu_ssl_keyfile = lookup('CONFIG_AODH_SSL_KEY', undef, undef, undef)
    $kombu_ssl_certfile = lookup('CONFIG_AODH_SSL_CERT', undef, undef, undef)

    if $kombu_ssl_keyfile {
      $files_to_set_owner = [ $kombu_ssl_keyfile, $kombu_ssl_certfile ]
      file { $files_to_set_owner:
        owner   => 'aodh',
        group   => 'aodh',
        require => Package['aodh'],
      }
      File[$files_to_set_owner] ~> Service<| tag == 'aodh-service' |>
    }
    Service<| name == 'rabbitmq-server' |> -> Service<| tag == 'aodh-service' |>

    class { 'aodh::logging':
      debug => lookup('CONFIG_DEBUG_MODE'),
    }

    class { 'aodh::db':
      database_connection => os_database_connection({
        'dialect'  => 'mysql+pymysql',
        'host'     => lookup('CONFIG_MARIADB_HOST_URL'),
        'username' => 'aodh',
        'password' => lookup('CONFIG_AODH_DB_PW'),
        'database' => 'aodh',
      })
    }

    class { 'aodh':
      rabbit_use_ssl        => lookup('CONFIG_AMQP_SSL_ENABLED'),
      default_transport_url => os_transport_url({
        'transport' => 'rabbit',
        'host'      => lookup('CONFIG_AMQP_HOST_URL'),
        'port'      => lookup('CONFIG_AMQP_CLIENTS_PORT'),
        'username'  => lookup('CONFIG_AMQP_AUTH_USER'),
        'password'  => lookup('CONFIG_AMQP_AUTH_PASSWORD')
      }),
      kombu_ssl_ca_certs    => $kombu_ssl_ca_certs,
      kombu_ssl_keyfile     => $kombu_ssl_keyfile,
      kombu_ssl_certfile    => $kombu_ssl_certfile,
    }
}
