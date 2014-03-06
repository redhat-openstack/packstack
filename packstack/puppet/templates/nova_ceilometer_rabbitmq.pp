
class { 'ceilometer':
    metering_secret  => '%(CONFIG_CEILOMETER_SECRET)s',
    rabbit_host      => '%(CONFIG_AMQP_HOST)s',
    rabbit_userid    => '%(CONFIG_AMQP_AUTH_USER)s',
    rabbit_password  => '%(CONFIG_AMQP_AUTH_PASSWORD)s',
    verbose          => true,
    debug            => %(CONFIG_DEBUG_MODE)s
}

