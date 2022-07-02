class packstack::nova::ceilometer::rabbitmq ()
{
    $ceilometer_kombu_ssl_ca_certs = lookup('CONFIG_AMQP_SSL_CACERT_FILE', undef, undef, undef)
    $ceilometer_kombu_ssl_keyfile = lookup('CONFIG_CEILOMETER_SSL_KEY', undef, undef, undef)
    $ceilometer_kombu_ssl_certfile = lookup('CONFIG_CEILOMETER_SSL_CERT', undef, undef, undef)

    $rabbit_host = lookup('CONFIG_AMQP_HOST_URL')
    $rabbit_port = lookup('CONFIG_AMQP_CLIENTS_PORT')
    $rabbit_userid = lookup('CONFIG_AMQP_AUTH_USER')
    $rabbit_password = lookup('CONFIG_AMQP_AUTH_PASSWORD')

    if $ceilometer_kombu_ssl_keyfile {
      $ceilometer_files_to_set_owner = [ $ceilometer_kombu_ssl_keyfile, $ceilometer_kombu_ssl_certfile ]
      file { $ceilometer_files_to_set_owner:
        owner   => 'ceilometer',
        group   => 'ceilometer',
        require => Package['nova-common'],
      }
      File[$ceilometer_files_to_set_owner] ~> Service<| tag == 'ceilometer-service' |>
    }
    Service<| name == 'rabbitmq-server' |> -> Service<| tag == 'ceilometer-service' |>

    class { 'ceilometer::logging':
        debug => lookup('CONFIG_DEBUG_MODE'),
    }

    class { 'ceilometer':
        telemetry_secret      => lookup('CONFIG_CEILOMETER_SECRET'),
        rabbit_use_ssl        => lookup('CONFIG_AMQP_SSL_ENABLED'),
        default_transport_url => "rabbit://${rabbit_userid}:${rabbit_password}@${rabbit_host}:${rabbit_port}/",
        # for some strange reason ceilometer needs to be in nova group
        require               => Package['nova-common'],
        kombu_ssl_ca_certs    => $ceilometer_kombu_ssl_ca_certs,
        kombu_ssl_keyfile     => $ceilometer_kombu_ssl_keyfile,
        kombu_ssl_certfile    => $ceilometer_kombu_ssl_certfile,
    }
}
