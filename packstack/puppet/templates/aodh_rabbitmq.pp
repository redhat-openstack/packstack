$kombu_ssl_ca_certs = hiera('CONFIG_AMQP_SSL_CACERT_FILE', undef)
$kombu_ssl_keyfile = hiera('CONFIG_AODH_SSL_KEY', undef)
$kombu_ssl_certfile = hiera('CONFIG_AODH_SSL_CERT', undef)

if $kombu_ssl_keyfile {
  $files_to_set_owner = [ $kombu_ssl_keyfile, $kombu_ssl_certfile ]
  file { $files_to_set_owner:
    owner   => 'aodh',
    group   => 'aodh',
    require => Package['openstack-aodh-common'],
  }
  File[$files_to_set_owner] ~> Service<||>
}

$config_mongodb_host = hiera('CONFIG_MONGODB_HOST_URL')

class { '::aodh':
  verbose            => true,
  debug              => hiera('CONFIG_DEBUG_MODE'),
  rabbit_host        => hiera('CONFIG_AMQP_HOST_URL'),
  rabbit_port        => hiera('CONFIG_AMQP_CLIENTS_PORT'),
  rabbit_use_ssl     => hiera('CONFIG_AMQP_SSL_ENABLED'),
  rabbit_userid      => hiera('CONFIG_AMQP_AUTH_USER'),
  rabbit_password    => hiera('CONFIG_AMQP_AUTH_PASSWORD'),
  kombu_ssl_ca_certs => $kombu_ssl_ca_certs,
  kombu_ssl_keyfile  => $kombu_ssl_keyfile,
  kombu_ssl_certfile => $kombu_ssl_certfile,
  database_connection => "mongodb://${config_mongodb_host}:27017/aodh",
}
