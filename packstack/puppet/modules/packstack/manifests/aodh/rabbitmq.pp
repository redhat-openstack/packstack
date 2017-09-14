class packstack::aodh::rabbitmq ()
{
    $kombu_ssl_ca_certs = hiera('CONFIG_AMQP_SSL_CACERT_FILE', undef)
    $kombu_ssl_keyfile = hiera('CONFIG_AODH_SSL_KEY', undef)
    $kombu_ssl_certfile = hiera('CONFIG_AODH_SSL_CERT', undef)

    $aodh_db_pw = hiera('CONFIG_AODH_DB_PW')
    $aodh_mariadb_host = hiera('CONFIG_MARIADB_HOST_URL')

    $rabbit_host = hiera('CONFIG_AMQP_HOST_URL')
    $rabbit_port = hiera('CONFIG_AMQP_CLIENTS_PORT')
    $rabbit_userid = hiera('CONFIG_AMQP_AUTH_USER')
    $rabbit_password = hiera('CONFIG_AMQP_AUTH_PASSWORD')


    if $kombu_ssl_keyfile {
      $files_to_set_owner = [ $kombu_ssl_keyfile, $kombu_ssl_certfile ]
      file { $files_to_set_owner:
        owner   => 'aodh',
        group   => 'aodh',
        require => Package['aodh'],
      }
      File[$files_to_set_owner] ~> Service<| tag == 'aodh-service' |>
    }

    class { '::aodh':
      debug              => hiera('CONFIG_DEBUG_MODE'),
      rabbit_use_ssl     => hiera('CONFIG_AMQP_SSL_ENABLED'),
      default_transport_url => "rabbit://${rabbit_userid}:${rabbit_password}@${rabbit_host}:${rabbit_port}/",
      kombu_ssl_ca_certs => $kombu_ssl_ca_certs,
      kombu_ssl_keyfile  => $kombu_ssl_keyfile,
      kombu_ssl_certfile => $kombu_ssl_certfile,
      database_connection => "mysql+pymysql://aodh:${aodh_db_pw}@${aodh_mariadb_host}/aodh",
    }
}
