class packstack::swift::ceilometer ()
{
    $rabbit_host = hiera('CONFIG_AMQP_HOST_URL')
    $rabbit_port = hiera('CONFIG_AMQP_CLIENTS_PORT')
    $rabbit_userid = hiera('CONFIG_AMQP_AUTH_USER')
    $rabbit_password = hiera('CONFIG_AMQP_AUTH_PASSWORD')

    class { '::swift::proxy::ceilometer':
      default_transport_url => "rabbit://${rabbit_userid}:${rabbit_password}@${rabbit_host}:${rabbit_port}/",
      topic                 => 'notifications',
      control_exchange      => 'swift',
      driver                => 'messaging',
      ignore_projects       => ['service'],
      auth_uri              => hiera('CONFIG_KEYSTONE_PUBLIC_URL'),
      auth_url              => hiera('CONFIG_KEYSTONE_ADMIN_URL'),
      password              => hiera('CONFIG_SWIFT_KS_PW'),
    }
}
