class { 'ceilometer':
    metering_secret => '%(CONFIG_CEILOMETER_SECRET)s',
    verbose         => true,
    debug           => %(CONFIG_DEBUG_MODE)s,
    rabbit_host     => '%(CONFIG_AMQP_HOST)s',
    rabbit_port     => '%(CONFIG_AMQP_CLIENTS_PORT)s',
    rabbit_use_ssl  => %(CONFIG_AMQP_ENABLE_SSL)s,
    rabbit_userid   => '%(CONFIG_AMQP_AUTH_USER)s',
    rabbit_password => '%(CONFIG_AMQP_AUTH_PASSWORD)s',
}
