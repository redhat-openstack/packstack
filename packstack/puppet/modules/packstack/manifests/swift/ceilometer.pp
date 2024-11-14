class packstack::swift::ceilometer ()
{
    Service<| name == 'rabbitmq-server' |> -> Service['swift-proxy-server']

    class { 'swift::proxy::ceilometer':
      default_transport_url => os_transport_url({
        'transport' => 'rabbit',
        'host'      => lookup('CONFIG_AMQP_HOST_URL'),
        'port'      => lookup('CONFIG_AMQP_CLIENTS_PORT'),
        'username'  => lookup('CONFIG_AMQP_AUTH_USER'),
        'password'  => lookup('CONFIG_AMQP_AUTH_PASSWORD')
      }),
      topic                 => 'notifications',
      control_exchange      => 'swift',
      driver                => 'messaging',
      ignore_projects       => ['service'],
      auth_url              => lookup('CONFIG_KEYSTONE_ADMIN_URL'),
      password              => lookup('CONFIG_SWIFT_KS_PW'),
    }
}
