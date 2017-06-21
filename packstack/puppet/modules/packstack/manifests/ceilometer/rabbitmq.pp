class packstack::ceilometer::rabbitmq ()
{
    $kombu_ssl_ca_certs = hiera('CONFIG_AMQP_SSL_CACERT_FILE', undef)
    $kombu_ssl_keyfile = hiera('CONFIG_CEILOMETER_SSL_KEY', undef)
    $kombu_ssl_certfile = hiera('CONFIG_CEILOMETER_SSL_CERT', undef)

    $rabbit_host = hiera('CONFIG_AMQP_HOST_URL')
    $rabbit_port = hiera('CONFIG_AMQP_CLIENTS_PORT')
    $rabbit_userid = hiera('CONFIG_AMQP_AUTH_USER')
    $rabbit_password = hiera('CONFIG_AMQP_AUTH_PASSWORD')

    if $kombu_ssl_keyfile {
      $files_to_set_owner = [ $kombu_ssl_keyfile, $kombu_ssl_certfile ]
      file { $files_to_set_owner:
        owner   => 'ceilometer',
        group   => 'ceilometer',
        require => Package['ceilometer-common'],
      }
      File[$files_to_set_owner] ~> Service<| tag == 'ceilometer-service' |>
    }

    class { '::ceilometer':
      telemetry_secret   => hiera('CONFIG_CEILOMETER_SECRET'),
      debug              => hiera('CONFIG_DEBUG_MODE'),
      rabbit_use_ssl     => hiera('CONFIG_AMQP_SSL_ENABLED'),
      default_transport_url => "rabbit://${rabbit_userid}:${rabbit_password}@${rabbit_host}:${rabbit_port}/",
      kombu_ssl_ca_certs => $kombu_ssl_ca_certs,
      kombu_ssl_keyfile  => $kombu_ssl_keyfile,
      kombu_ssl_certfile => $kombu_ssl_certfile,
    }
}
