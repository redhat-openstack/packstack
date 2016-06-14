class packstack::swift::ceilometer ()
{
    class { '::swift::proxy::ceilometer':
      rabbit_user      => hiera('CONFIG_AMQP_AUTH_USER'),
      rabbit_password  => hiera('CONFIG_AMQP_AUTH_PASSWORD'),
      rabbit_host      => hiera('CONFIG_AMQP_HOST_URL'),
      rabbit_port      => hiera('CONFIG_AMQP_CLIENTS_PORT'),
      topic            => 'notifications',
      control_exchange => 'swift',
      driver           => 'messaging',
    }
}
