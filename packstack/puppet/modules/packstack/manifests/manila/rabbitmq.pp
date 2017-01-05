class packstack::manila::rabbitmq ()
{
    $kombu_ssl_ca_certs = hiera('CONFIG_AMQP_SSL_CACERT_FILE', undef)
    $kombu_ssl_keyfile = hiera('CONFIG_MANILA_SSL_KEY', undef)
    $kombu_ssl_certfile = hiera('CONFIG_MANILA_SSL_CERT', undef)

    $rabbit_host = hiera('CONFIG_AMQP_HOST_URL')
    $rabbit_port = hiera('CONFIG_AMQP_CLIENTS_PORT')
    $rabbit_userid = hiera('CONFIG_AMQP_AUTH_USER')
    $rabbit_password = hiera('CONFIG_AMQP_AUTH_PASSWORD')

    if $kombu_ssl_keyfile {
      $files_to_set_owner = [ $kombu_ssl_keyfile, $kombu_ssl_certfile ]
      file { $files_to_set_owner:
        owner   => 'manila',
        group   => 'manila',
        # manila user on RH/Fedora is provided by python-manila
        require => Package['manila'],
      }
      File[$files_to_set_owner] ~> Service<| tag == 'manila-service' |>
    }

    $db_pw = hiera('CONFIG_MANILA_DB_PW')
    $mariadb_host = hiera('CONFIG_MARIADB_HOST_URL')

    class { '::manila':
      rabbit_use_ssl        => hiera('CONFIG_AMQP_SSL_ENABLED'),
      default_transport_url => "rabbit://${rabbit_userid}:${rabbit_password}@${rabbit_host}:${rabbit_port}/",
      sql_connection        => "mysql+pymysql://manila:${db_pw}@${mariadb_host}/manila",
      debug                 => hiera('CONFIG_DEBUG_MODE'),
    }
}
