
class {'cinder':
    rabbit_host      => "%(CONFIG_AMQP_HOST)s",
    rabbit_port      => '%(CONFIG_AMQP_CLIENTS_PORT)s',
    rabbit_userid    => '%(CONFIG_AMQP_AUTH_USER)s',
    rabbit_password  => '%(CONFIG_AMQP_AUTH_PASSWORD)s',
    sql_connection   => "mysql://cinder:%(CONFIG_CINDER_DB_PW)s@%(CONFIG_MARIADB_HOST)s/cinder",
    verbose          => true,
    debug            => %(CONFIG_DEBUG_MODE)s,
}
