$heat_rabbitmq_cfg_heat_db_pw = hiera('CONFIG_HEAT_DB_PW')
$heat_rabbitmq_cfg_mariadb_host = hiera('CONFIG_MARIADB_HOST_URL')

$kombu_ssl_ca_certs = hiera('CONFIG_AMQP_SSL_CACERT_FILE', $::os_service_default)
$kombu_ssl_keyfile = hiera('CONFIG_HEAT_SSL_KEY', $::os_service_default)
$kombu_ssl_certfile = hiera('CONFIG_HEAT_SSL_CERT', $::os_service_default)

if ! is_service_default($kombu_ssl_keyfile) {
  $files_to_set_owner = [ $kombu_ssl_keyfile, $kombu_ssl_certfile ]
  file { $files_to_set_owner:
    owner   => 'heat',
    group   => 'heat',
    require => Package['heat-common'],
  }
  File[$files_to_set_owner] ~> Service<||>
}

class { '::heat':
  keystone_password   => hiera('CONFIG_HEAT_KS_PW'),
  auth_uri            => hiera('CONFIG_KEYSTONE_PUBLIC_URL'),
  identity_uri        => hiera('CONFIG_KEYSTONE_ADMIN_URL'),
  keystone_ec2_uri    => hiera('CONFIG_KEYSTONE_PUBLIC_URL'),
  rpc_backend         => 'rabbit',
  rabbit_host         => hiera('CONFIG_AMQP_HOST_URL'),
  rabbit_port         => hiera('CONFIG_AMQP_CLIENTS_PORT'),
  rabbit_use_ssl      => hiera('CONFIG_AMQP_SSL_ENABLED'),
  rabbit_userid       => hiera('CONFIG_AMQP_AUTH_USER'),
  rabbit_password     => hiera('CONFIG_AMQP_AUTH_PASSWORD'),
  verbose             => true,
  debug               => hiera('CONFIG_DEBUG_MODE'),
  database_connection => "mysql+pymysql://heat:${heat_rabbitmq_cfg_heat_db_pw}@${heat_rabbitmq_cfg_mariadb_host}/heat",
  kombu_ssl_ca_certs  => $kombu_ssl_ca_certs,
  kombu_ssl_keyfile   => $kombu_ssl_keyfile,
  kombu_ssl_certfile  => $kombu_ssl_certfile,
}
