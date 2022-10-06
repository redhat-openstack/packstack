class packstack::cinder::rabbitmq ()
{
    $cinder_rab_cfg_cinder_db_pw = lookup('CONFIG_CINDER_DB_PW')
    $cinder_rab_cfg_mariadb_host = lookup('CONFIG_MARIADB_HOST_URL')

    $kombu_ssl_ca_certs = lookup('CONFIG_AMQP_SSL_CACERT_FILE', undef, undef, undef)
    $kombu_ssl_keyfile = lookup('CONFIG_CINDER_SSL_KEY', undef, undef, undef)
    $kombu_ssl_certfile = lookup('CONFIG_CINDER_SSL_CERT', undef, undef, undef)

    $rabbit_host = lookup('CONFIG_AMQP_HOST_URL')
    $rabbit_port = lookup('CONFIG_AMQP_CLIENTS_PORT')
    $rabbit_userid = lookup('CONFIG_AMQP_AUTH_USER')
    $rabbit_password = lookup('CONFIG_AMQP_AUTH_PASSWORD')

    if $kombu_ssl_keyfile {
      $files_to_set_owner = [ $kombu_ssl_keyfile, $kombu_ssl_certfile ]
      file { $files_to_set_owner:
        owner   => 'cinder',
        group   => 'cinder',
        require => Class['cinder'],
      }
      File[$files_to_set_owner] ~> Service<| tag == 'cinder-service' |>
    }
    Service<| name == 'rabbitmq-server' |> -> Service<| tag == 'cinder-service' |>

    class { 'cinder::logging':
      debug => lookup('CONFIG_DEBUG_MODE'),
    }

    class { 'cinder::db':
      database_connection   => "mysql+pymysql://cinder:${cinder_rab_cfg_cinder_db_pw}@${cinder_rab_cfg_mariadb_host}/cinder",
    }

    class { 'cinder':
      rabbit_use_ssl        => lookup('CONFIG_AMQP_SSL_ENABLED'),
      default_transport_url => "rabbit://${rabbit_userid}:${rabbit_password}@${rabbit_host}:${rabbit_port}/",
      kombu_ssl_ca_certs    => $kombu_ssl_ca_certs,
      kombu_ssl_keyfile     => $kombu_ssl_keyfile,
      kombu_ssl_certfile    => $kombu_ssl_certfile,
      notification_driver   => 'messagingv2',
    }
}
