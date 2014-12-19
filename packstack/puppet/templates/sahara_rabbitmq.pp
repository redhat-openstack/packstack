class { 'sahara::notify::rabbitmq':
  rabbit_host     => hiera('CONFIG_AMQP_HOST'),
  rabbit_port     => hiera('CONFIG_AMQP_CLIENTS_PORT'),
  rabbit_userid   => hiera('CONFIG_AMQP_AUTH_USER'),
  rabbit_password => hiera('CONFIG_AMQP_AUTH_PASSWORD'),
}
