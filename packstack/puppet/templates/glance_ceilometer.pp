
class { 'glance::notify::qpid':
    qpid_password => '%(CONFIG_QPID_AUTH_PASSWORD)s',
    qpid_username => '%(CONFIG_QPID_AUTH_USER)s',
    qpid_hostname => '%(CONFIG_QPID_HOST)s',
    qpid_port     => '%(CONFIG_QPID_CLIENTS_PORT)s',
    qpid_protocol => '%(CONFIG_QPID_PROTOCOL)s'
}
