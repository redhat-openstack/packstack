
class { 'ceilometer':
    metering_secret => hiera('CONFIG_CEILOMETER_SECRET'),
    rabbit_host     => hiera('CONFIG_AMQP_HOST'),
    rabbit_userid   => hiera('CONFIG_AMQP_AUTH_USER'),
    rabbit_password => hiera('CONFIG_AMQP_AUTH_PASSWORD'),
    verbose         => true,
    debug           => hiera('CONFIG_DEBUG_MODE'),
    # for some strange reason ceilometer needs to be in nova group
    require         => Package['nova-common'],
}

