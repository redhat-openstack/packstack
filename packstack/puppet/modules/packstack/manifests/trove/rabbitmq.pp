class packstack::trove::rabbitmq ()
{
    $trove_rabmq_cfg_trove_db_pw = lookup('CONFIG_TROVE_DB_PW')
    $trove_rabmq_cfg_mariadb_host = lookup('CONFIG_MARIADB_HOST_URL')
    $trove_rabmq_cfg_controller_host = lookup('CONFIG_KEYSTONE_HOST_URL')

    $kombu_ssl_ca_certs = lookup('CONFIG_AMQP_SSL_CACERT_FILE', undef, undef, undef)
    $kombu_ssl_keyfile = lookup('CONFIG_TROVE_SSL_KEY', undef, undef, undef)
    $kombu_ssl_certfile = lookup('CONFIG_TROVE_SSL_CERT', undef, undef, undef)

    $rabbit_host = lookup('CONFIG_AMQP_HOST_URL')
    $rabbit_port = lookup('CONFIG_AMQP_CLIENTS_PORT')
    $rabbit_userid = lookup('CONFIG_AMQP_AUTH_USER')
    $rabbit_password = lookup('CONFIG_AMQP_AUTH_PASSWORD')

    if $kombu_ssl_keyfile {
      $files_to_set_owner = [ $kombu_ssl_keyfile, $kombu_ssl_certfile ]
      file { $files_to_set_owner:
        owner => 'trove',
        group => 'trove',
      }
      Package<|tag=='trove'|> -> File[$files_to_set_owner]
      File[$files_to_set_owner] ~> Service<| tag == 'trove-service' |>
    }
    Service<| name == 'rabbitmq-server' |> -> Service<| tag == 'trove-service' |>

    class { 'trove::db':
      database_connection => "mysql+pymysql://trove:${trove_rabmq_cfg_trove_db_pw}@${trove_rabmq_cfg_mariadb_host}/trove",
    }

    class { 'trove':
      rabbit_use_ssl        => lookup('CONFIG_AMQP_SSL_ENABLED'),
      default_transport_url => "rabbit://${rabbit_userid}:${rabbit_password}@${rabbit_host}:${rabbit_port}/",
      kombu_ssl_ca_certs    => $kombu_ssl_ca_certs,
      kombu_ssl_keyfile     => $kombu_ssl_keyfile,
      kombu_ssl_certfile    => $kombu_ssl_certfile,
    }
}
