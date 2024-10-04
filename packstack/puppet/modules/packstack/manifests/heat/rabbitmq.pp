class packstack::heat::rabbitmq ()
{
    $heat_rabbitmq_cfg_heat_db_pw = lookup('CONFIG_HEAT_DB_PW')
    $heat_rabbitmq_cfg_mariadb_host = lookup('CONFIG_MARIADB_HOST_URL')

    $kombu_ssl_ca_certs = lookup('CONFIG_AMQP_SSL_CACERT_FILE', undef, undef, undef)
    $kombu_ssl_keyfile = lookup('CONFIG_HEAT_SSL_KEY', undef, undef, undef)
    $kombu_ssl_certfile = lookup('CONFIG_HEAT_SSL_CERT', undef, undef, undef)

    $rabbit_host = lookup('CONFIG_AMQP_HOST_URL')
    $rabbit_port = lookup('CONFIG_AMQP_CLIENTS_PORT')
    $rabbit_userid = lookup('CONFIG_AMQP_AUTH_USER')
    $rabbit_password = lookup('CONFIG_AMQP_AUTH_PASSWORD')

    if $kombu_ssl_keyfile {
      $files_to_set_owner = [ $kombu_ssl_keyfile, $kombu_ssl_certfile ]
      file { $files_to_set_owner:
        owner   => 'heat',
        group   => 'heat',
        require => Package['heat-common'],
      }
      File[$files_to_set_owner] ~> Service<| tag == 'heat-service' |>
    }
    Service<| name == 'rabbitmq-server' |> -> Service<| tag == 'heat-service' |>

    if lookup('CONFIG_CEILOMETER_INSTALL') == 'y' {
      $heat_notification_driver = 'messagingv2'
    } else {
      $heat_notification_driver = $facts['os_service_default']
    }

    class { 'heat::trustee':
      password => lookup('CONFIG_HEAT_KS_PW'),
      auth_url => lookup('CONFIG_KEYSTONE_ADMIN_URL'),
    }
    class { 'heat::keystone::authtoken':
      password             => lookup('CONFIG_HEAT_KS_PW'),
      www_authenticate_uri => lookup('CONFIG_KEYSTONE_PUBLIC_URL_VERSIONLESS'),
      auth_url             => lookup('CONFIG_KEYSTONE_ADMIN_URL'),
    }

    class { 'heat::logging':
      debug => lookup('CONFIG_DEBUG_MODE'),
    }

    class { 'heat::db':
      database_connection => "mysql+pymysql://heat:${heat_rabbitmq_cfg_heat_db_pw}@${heat_rabbitmq_cfg_mariadb_host}/heat",
    }

    class { 'heat':
      keystone_ec2_uri      => lookup('CONFIG_KEYSTONE_PUBLIC_URL'),
      rabbit_use_ssl        => lookup('CONFIG_AMQP_SSL_ENABLED'),
      default_transport_url => "rabbit://${rabbit_userid}:${rabbit_password}@${rabbit_host}:${rabbit_port}/",
      kombu_ssl_ca_certs    => $kombu_ssl_ca_certs,
      kombu_ssl_keyfile     => $kombu_ssl_keyfile,
      kombu_ssl_certfile    => $kombu_ssl_certfile,
      notification_driver   => $heat_notification_driver,
    }
}
