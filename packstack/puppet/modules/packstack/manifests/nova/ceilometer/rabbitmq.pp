class packstack::nova::ceilometer::rabbitmq ()
{
    $kombu_ssl_ca_certs = lookup('CONFIG_AMQP_SSL_CACERT_FILE', undef, undef, undef)
    $kombu_ssl_keyfile = lookup('CONFIG_CEILOMETER_SSL_KEY', undef, undef, undef)
    $kombu_ssl_certfile = lookup('CONFIG_CEILOMETER_SSL_CERT', undef, undef, undef)

    if $kombu_ssl_keyfile {
      $files_to_set_owner = [ $kombu_ssl_keyfile, $kombu_ssl_certfile ]
      file { $files_to_set_owner:
        owner   => 'ceilometer',
        group   => 'ceilometer',
        require => Package['nova-common'],
      }
      File[$files_to_set_owner] ~> Service<| tag == 'ceilometer-service' |>
    }
    Service<| name == 'rabbitmq-server' |> -> Service<| tag == 'ceilometer-service' |>

    class { 'ceilometer::logging':
        debug => lookup('CONFIG_DEBUG_MODE'),
    }

    class { 'ceilometer':
      telemetry_secret      => lookup('CONFIG_CEILOMETER_SECRET'),
      rabbit_use_ssl        => lookup('CONFIG_AMQP_SSL_ENABLED'),
      default_transport_url => os_transport_url({
        'transport' => 'rabbit',
        'host'      => lookup('CONFIG_AMQP_HOST_URL'),
        'port'      => lookup('CONFIG_AMQP_CLIENTS_PORT'),
        'username'  => lookup('CONFIG_AMQP_AUTH_USER'),
        'password'  => lookup('CONFIG_AMQP_AUTH_PASSWORD')
      }),
      # for some strange reason ceilometer needs to be in nova group
      require               => Package['nova-common'],
      kombu_ssl_ca_certs    => $kombu_ssl_ca_certs,
      kombu_ssl_keyfile     => $kombu_ssl_keyfile,
      kombu_ssl_certfile    => $kombu_ssl_certfile,
    }
}
