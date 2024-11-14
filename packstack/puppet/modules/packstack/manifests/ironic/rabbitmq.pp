class packstack::ironic::rabbitmq ()
{
    $kombu_ssl_ca_certs = lookup('CONFIG_AMQP_SSL_CACERT_FILE', undef, undef, undef)
    $kombu_ssl_keyfile = lookup('CONFIG_IRONIC_SSL_KEY', undef, undef, undef)
    $kombu_ssl_certfile = lookup('CONFIG_IRONIC_SSL_CERT', undef, undef, undef)

    if $kombu_ssl_keyfile {
      $files_to_set_owner = [ $kombu_ssl_keyfile, $kombu_ssl_certfile ]
      file { $files_to_set_owner:
        owner   => 'ironic',
        group   => 'ironic',
        require => Package['ironic-common'],
      }
      File[$files_to_set_owner] ~> Service<| tag == 'ironic-service' |>
    }
    Service<| name == 'rabbitmq-server' |> -> Service<| tag == 'ironic-service' |>

    class { 'ironic::logging':
      debug => true,
    }

    class { 'ironic::db':
      database_connection => os_database_connection({
        'dialect'  => 'mysql+pymysql',
        'host'     => lookup('CONFIG_MARIADB_HOST_URL'),
        'username' => 'ironic',
        'password' => lookup('CONFIG_IRONIC_DB_PW'),
        'database' => 'ironic',
      })
    }

    class { 'ironic':
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
