class packstack::sahara::rabbitmq ()
{
    $sahara_cfg_sahara_db_pw = lookup('CONFIG_SAHARA_DB_PW')
    $sahara_cfg_sahara_mariadb_host = lookup('CONFIG_MARIADB_HOST_URL')

    $kombu_ssl_ca_certs = lookup('CONFIG_AMQP_SSL_CACERT_FILE', undef, undef, $::os_service_default)
    $kombu_ssl_keyfile = lookup('CONFIG_SAHARA_SSL_KEY', undef, undef, $::os_service_default)
    $kombu_ssl_certfile = lookup('CONFIG_SAHARA_SSL_CERT', undef, undef, $::os_service_default)

    $rabbit_host = lookup('CONFIG_AMQP_HOST_URL')
    $rabbit_port = lookup('CONFIG_AMQP_CLIENTS_PORT')
    $rabbit_userid = lookup('CONFIG_AMQP_AUTH_USER')
    $rabbit_password = lookup('CONFIG_AMQP_AUTH_PASSWORD')

    if ! is_service_default($kombu_ssl_keyfile) {
      $files_to_set_owner = [ $kombu_ssl_keyfile, $kombu_ssl_certfile ]
      file { $files_to_set_owner:
        owner   => 'sahara',
        group   => 'sahara',
        require => Package['sahara-common'],
      }
      File[$files_to_set_owner] ~> Service<| tag == 'sahara-service' |>
    }
    Service<| name == 'rabbitmq-server' |> -> Service<| tag == 'sahara-service' |>

    class { 'sahara::keystone::authtoken':
      username             => 'sahara',
      password             => lookup('CONFIG_SAHARA_KS_PW'),
      project_name         => 'services',
      www_authenticate_uri => lookup('CONFIG_KEYSTONE_PUBLIC_URL'),
      auth_url             => lookup('CONFIG_KEYSTONE_ADMIN_URL'),
    }

    class { 'sahara::logging':
      debug => lookup('CONFIG_DEBUG_MODE'),
    }

    class { 'sahara::db':
      database_connection => "mysql+pymysql://sahara:${sahara_cfg_sahara_db_pw}@${sahara_cfg_sahara_mariadb_host}/sahara",
    }

    class { 'sahara':
      host                  => lookup('CONFIG_SAHARA_HOST'),
      rabbit_use_ssl        => lookup('CONFIG_AMQP_SSL_ENABLED'),
      default_transport_url => "rabbit://${rabbit_userid}:${rabbit_password}@${rabbit_host}:${rabbit_port}/",
      kombu_ssl_ca_certs    => $kombu_ssl_ca_certs,
      kombu_ssl_keyfile     => $kombu_ssl_keyfile,
      kombu_ssl_certfile    => $kombu_ssl_certfile,
    }
}
