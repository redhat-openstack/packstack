class packstack::swift::ceilometer ()
{
    $rabbit_host = lookup('CONFIG_AMQP_HOST_URL')
    $rabbit_port = lookup('CONFIG_AMQP_CLIENTS_PORT')
    $rabbit_userid = lookup('CONFIG_AMQP_AUTH_USER')
    $rabbit_password = lookup('CONFIG_AMQP_AUTH_PASSWORD')

    Service<| name == 'rabbitmq-server' |> -> Service['swift-proxy-server']

    class { 'swift::proxy::ceilometer':
      default_transport_url => "rabbit://${rabbit_userid}:${rabbit_password}@${rabbit_host}:${rabbit_port}/",
      topic                 => 'notifications',
      control_exchange      => 'swift',
      driver                => 'messaging',
      ignore_projects       => ['service'],
      auth_url              => lookup('CONFIG_KEYSTONE_ADMIN_URL'),
      password              => lookup('CONFIG_SWIFT_KS_PW'),
    }
}
