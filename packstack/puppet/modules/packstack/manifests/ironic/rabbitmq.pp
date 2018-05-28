class packstack::ironic::rabbitmq ()
{
    $ironic_rabbitmq_cfg_ironic_db_pw = hiera('CONFIG_IRONIC_DB_PW')
    $ironic_rabbitmq_cfg_mariadb_host = hiera('CONFIG_MARIADB_HOST_URL')

    $kombu_ssl_ca_certs = hiera('CONFIG_AMQP_SSL_CACERT_FILE', undef)
    $kombu_ssl_keyfile = hiera('CONFIG_IRONIC_SSL_KEY', undef)
    $kombu_ssl_certfile = hiera('CONFIG_IRONIC_SSL_CERT', undef)

    $rabbit_host = hiera('CONFIG_AMQP_HOST_URL')
    $rabbit_port = hiera('CONFIG_AMQP_CLIENTS_PORT')
    $rabbit_userid = hiera('CONFIG_AMQP_AUTH_USER')
    $rabbit_password = hiera('CONFIG_AMQP_AUTH_PASSWORD')

    if $kombu_ssl_keyfile {
      $files_to_set_owner = [ $kombu_ssl_keyfile, $kombu_ssl_certfile ]
      file { $files_to_set_owner:
        owner   => 'ironic',
        group   => 'ironic',
        require => Package['ironic-common'],
      }
      File[$files_to_set_owner] ~> Service<| tag == 'ironic-service' |>
    }

    class { '::ironic':
      rabbit_use_ssl        => hiera('CONFIG_AMQP_SSL_ENABLED'),
      default_transport_url => "rabbit://${rabbit_userid}:${rabbit_password}@${rabbit_host}:${rabbit_port}/",
      database_connection   => "mysql+pymysql://ironic:${ironic_rabbitmq_cfg_ironic_db_pw}@${ironic_rabbitmq_cfg_mariadb_host}/ironic",
      debug                 => true,
      kombu_ssl_ca_certs    => $kombu_ssl_ca_certs,
      kombu_ssl_keyfile     => $kombu_ssl_keyfile,
      kombu_ssl_certfile    => $kombu_ssl_certfile,
    }
}
