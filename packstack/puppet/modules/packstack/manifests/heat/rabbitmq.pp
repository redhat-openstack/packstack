class packstack::heat::rabbitmq ()
{
    $heat_rabbitmq_cfg_heat_db_pw = hiera('CONFIG_HEAT_DB_PW')
    $heat_rabbitmq_cfg_mariadb_host = hiera('CONFIG_MARIADB_HOST_URL')

    $kombu_ssl_ca_certs = hiera('CONFIG_AMQP_SSL_CACERT_FILE', $::os_service_default)
    $kombu_ssl_keyfile = hiera('CONFIG_HEAT_SSL_KEY', $::os_service_default)
    $kombu_ssl_certfile = hiera('CONFIG_HEAT_SSL_CERT', $::os_service_default)

    $rabbit_host = hiera('CONFIG_AMQP_HOST_URL')
    $rabbit_port = hiera('CONFIG_AMQP_CLIENTS_PORT')
    $rabbit_userid = hiera('CONFIG_AMQP_AUTH_USER')
    $rabbit_password = hiera('CONFIG_AMQP_AUTH_PASSWORD')

    if ! is_service_default($kombu_ssl_keyfile) {
      $files_to_set_owner = [ $kombu_ssl_keyfile, $kombu_ssl_certfile ]
      file { $files_to_set_owner:
        owner   => 'heat',
        group   => 'heat',
        require => Package['heat-common'],
      }
      File[$files_to_set_owner] ~> Service<| tag == 'heat-service' |>
    }

    if hiera('CONFIG_CEILOMETER_INSTALL') == 'y' {
      $heat_notification_driver = 'messagingv2'
    } else {
      $heat_notification_driver = $::os_service_default
    }

    class { '::heat::keystone::authtoken':
      password   => hiera('CONFIG_HEAT_KS_PW'),
      auth_uri   => hiera('CONFIG_KEYSTONE_PUBLIC_URL'),
      auth_url   => hiera('CONFIG_KEYSTONE_ADMIN_URL'),
    }

    class { '::heat':
      keystone_ec2_uri    => hiera('CONFIG_KEYSTONE_PUBLIC_URL'),
      rabbit_use_ssl      => hiera('CONFIG_AMQP_SSL_ENABLED'),
      default_transport_url => "rabbit://${rabbit_userid}:${rabbit_password}@${rabbit_host}:${rabbit_port}/",
      debug               => hiera('CONFIG_DEBUG_MODE'),
      database_connection => "mysql+pymysql://heat:${heat_rabbitmq_cfg_heat_db_pw}@${heat_rabbitmq_cfg_mariadb_host}/heat",
      kombu_ssl_ca_certs  => $kombu_ssl_ca_certs,
      kombu_ssl_keyfile   => $kombu_ssl_keyfile,
      kombu_ssl_certfile  => $kombu_ssl_certfile,
      notification_driver => $heat_notification_driver,
    }
}
