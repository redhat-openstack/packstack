class packstack::glance::ceilometer ()
{
    $kombu_ssl_ca_certs = lookup('CONFIG_AMQP_SSL_CACERT_FILE', undef, undef, undef)
    $kombu_ssl_keyfile = lookup('CONFIG_GLANCE_SSL_KEY', undef, undef, undef)
    $kombu_ssl_certfile = lookup('CONFIG_GLANCE_SSL_CERT', undef, undef, undef)

    if $kombu_ssl_keyfile {
      $files_to_set_owner = [ $kombu_ssl_keyfile, $kombu_ssl_certfile ]
      file { $files_to_set_owner:
        owner   => 'glance',
        group   => 'glance',
        require => Class['::glance::notify::rabbitmq'],
        notify  => Service['glance-api'],
      }
    }
    Service<| name == 'rabbitmq-server' |> -> Service['glance-api']

    class { 'glance::notify::rabbitmq':
      rabbit_notification_topic => 'notifications',
      rabbit_use_ssl            => lookup('CONFIG_AMQP_SSL_ENABLED'),
      default_transport_url     => os_transport_url({
        'transport' => 'rabbit',
        'host'      => lookup('CONFIG_AMQP_HOST_URL'),
        'port'      => lookup('CONFIG_AMQP_CLIENTS_PORT'),
        'username'  => lookup('CONFIG_AMQP_AUTH_USER'),
        'password'  => lookup('CONFIG_AMQP_AUTH_PASSWORD')
      }),
      kombu_ssl_ca_certs        => $kombu_ssl_ca_certs,
      kombu_ssl_keyfile         => $kombu_ssl_keyfile,
      kombu_ssl_certfile        => $kombu_ssl_certfile,
      notification_driver       => 'messagingv2',
    }
}
