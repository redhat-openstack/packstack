$cinder_rab_cfg_cinder_db_pw = hiera('CONFIG_CINDER_DB_PW')
$cinder_rab_cfg_mariadb_host = hiera('CONFIG_MARIADB_HOST')

class {'cinder':
  rabbit_host         => hiera('CONFIG_AMQP_HOST'),
  rabbit_port         => hiera('CONFIG_AMQP_CLIENTS_PORT'),
  rabbit_userid       => hiera('CONFIG_AMQP_AUTH_USER'),
  rabbit_password     => hiera('CONFIG_AMQP_AUTH_PASSWORD'),
  database_connection => "mysql://cinder:${cinder_rab_cfg_cinder_db_pw}@${cinder_rab_cfg_mariadb_host}/cinder",
  verbose             => true,
  debug               => hiera('CONFIG_DEBUG_MODE'),
}
