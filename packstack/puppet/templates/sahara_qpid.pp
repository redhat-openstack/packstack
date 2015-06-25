class { '::sahara::notify::qpid':
  qpid_hostname => hiera('CONFIG_AMQP_HOST_URL'),
  qpid_port     => hiera('CONFIG_AMQP_CLIENTS_PORT'),
  qpid_protocol => hiera('CONFIG_AMQP_PROTOCOL'),
  qpid_username => hiera('CONFIG_AMQP_AUTH_USER'),
  qpid_password => hiera('CONFIG_AMQP_AUTH_PASSWORD'),
}
