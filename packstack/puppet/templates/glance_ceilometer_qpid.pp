
class { 'glance::notify::qpid':
  qpid_password => hiera('CONFIG_AMQP_AUTH_PASSWORD'),
  qpid_username => hiera('CONFIG_AMQP_AUTH_USER'),
  qpid_hostname => hiera('CONFIG_AMQP_HOST'),
  qpid_port     => hiera('CONFIG_AMQP_CLIENTS_PORT'),
  qpid_protocol => hiera('CONFIG_AMQP_PROTOCOL'),
}
