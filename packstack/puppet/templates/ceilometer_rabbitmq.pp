class { '::ceilometer':
  metering_secret => hiera('CONFIG_CEILOMETER_SECRET'),
  verbose         => true,
  debug           => hiera('CONFIG_DEBUG_MODE'),
  rabbit_host     => hiera('CONFIG_AMQP_HOST_URL'),
  rabbit_port     => hiera('CONFIG_AMQP_CLIENTS_PORT'),
  rabbit_use_ssl  => hiera('CONFIG_AMQP_ENABLE_SSL'),
  rabbit_userid   => hiera('CONFIG_AMQP_AUTH_USER'),
  rabbit_password => hiera('CONFIG_AMQP_AUTH_PASSWORD'),
}
