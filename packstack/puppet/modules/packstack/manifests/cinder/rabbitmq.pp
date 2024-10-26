class packstack::cinder::rabbitmq ()
{
    $kombu_ssl_ca_certs = lookup('CONFIG_AMQP_SSL_CACERT_FILE', undef, undef, undef)
    $kombu_ssl_keyfile = lookup('CONFIG_CINDER_SSL_KEY', undef, undef, undef)
    $kombu_ssl_certfile = lookup('CONFIG_CINDER_SSL_CERT', undef, undef, undef)

    if $kombu_ssl_keyfile {
      $files_to_set_owner = [ $kombu_ssl_keyfile, $kombu_ssl_certfile ]
      file { $files_to_set_owner:
        owner   => 'cinder',
        group   => 'cinder',
        require => Class['cinder'],
      }
      File[$files_to_set_owner] ~> Service<| tag == 'cinder-service' |>
    }
    Service<| name == 'rabbitmq-server' |> -> Service<| tag == 'cinder-service' |>

    class { 'cinder::logging':
      debug => lookup('CONFIG_DEBUG_MODE'),
    }

    class { 'cinder::db':
      database_connection => os_database_connection({
        'dialect'  => 'mysql+pymysql',
        'host'     => lookup('CONFIG_MARIADB_HOST_URL'),
        'username' => 'cinder',
        'password' => lookup('CONFIG_CINDER_DB_PW'),
        'database' => 'cinder',
      })
    }

    class { 'cinder':
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
      notification_driver   => 'messagingv2',
    }
}
