class packstack::manila::rabbitmq ()
{
    $kombu_ssl_ca_certs = lookup('CONFIG_AMQP_SSL_CACERT_FILE', undef, undef, undef)
    $kombu_ssl_keyfile = lookup('CONFIG_MANILA_SSL_KEY', undef, undef, undef)
    $kombu_ssl_certfile = lookup('CONFIG_MANILA_SSL_CERT', undef, undef, undef)

    $rabbit_host = lookup('CONFIG_AMQP_HOST_URL')
    $rabbit_port = lookup('CONFIG_AMQP_CLIENTS_PORT')
    $rabbit_userid = lookup('CONFIG_AMQP_AUTH_USER')
    $rabbit_password = lookup('CONFIG_AMQP_AUTH_PASSWORD')

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
    Service<| name == 'rabbitmq-server' |> -> Service<| tag == 'manila-service' |>

    $db_pw = lookup('CONFIG_MANILA_DB_PW')
    $mariadb_host = lookup('CONFIG_MARIADB_HOST_URL')

    class { 'manila::logging':
      debug => lookup('CONFIG_DEBUG_MODE'),
    }

    class { 'manila::db':
      database_connection => "mysql+pymysql://manila:${db_pw}@${mariadb_host}/manila",
    }

    class { 'manila':
      rabbit_use_ssl        => lookup('CONFIG_AMQP_SSL_ENABLED'),
      default_transport_url => "rabbit://${rabbit_userid}:${rabbit_password}@${rabbit_host}:${rabbit_port}/",
    }
}
