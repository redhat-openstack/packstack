
class { 'glance::notify::qpid':
    qpid_password => '%(CONFIG_AMQP_AUTH_PASSWORD)s',
    qpid_username => '%(CONFIG_AMQP_AUTH_USER)s',
    qpid_hostname => '%(CONFIG_AMQP_HOST)s',
    qpid_port     => '%(CONFIG_AMQP_CLIENTS_PORT)s',
    qpid_protocol => '%(CONFIG_AMQP_PROTOCOL)s'
}
