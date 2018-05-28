class packstack::sahara::rabbitmq ()
{
    $sahara_cfg_sahara_db_pw = hiera('CONFIG_SAHARA_DB_PW')
    $sahara_cfg_sahara_mariadb_host = hiera('CONFIG_MARIADB_HOST_URL')
    $sahara_cfg_config_neutron_install = hiera('CONFIG_NEUTRON_INSTALL')

    $kombu_ssl_ca_certs = hiera('CONFIG_AMQP_SSL_CACERT_FILE', $::os_service_default)
    $kombu_ssl_keyfile = hiera('CONFIG_SAHARA_SSL_KEY', $::os_service_default)
    $kombu_ssl_certfile = hiera('CONFIG_SAHARA_SSL_CERT', $::os_service_default)

    $rabbit_host = hiera('CONFIG_AMQP_HOST_URL')
    $rabbit_port = hiera('CONFIG_AMQP_CLIENTS_PORT')
    $rabbit_userid = hiera('CONFIG_AMQP_AUTH_USER')
    $rabbit_password = hiera('CONFIG_AMQP_AUTH_PASSWORD')

    if ! is_service_default($kombu_ssl_keyfile) {
      $files_to_set_owner = [ $kombu_ssl_keyfile, $kombu_ssl_certfile ]
      file { $files_to_set_owner:
        owner   => 'sahara',
        group   => 'sahara',
        require => Package['sahara-common'],
      }
      File[$files_to_set_owner] ~> Service<| tag == 'sahara-service' |>
    }

    class { '::sahara':
      database_connection   =>
        "mysql+pymysql://sahara:${sahara_cfg_sahara_db_pw}@${sahara_cfg_sahara_mariadb_host}/sahara",
      debug                 => hiera('CONFIG_DEBUG_MODE'),
      admin_user            => 'sahara',
      admin_password        => hiera('CONFIG_SAHARA_KS_PW'),
      admin_tenant_name     => 'services',
      auth_uri              => hiera('CONFIG_KEYSTONE_PUBLIC_URL'),
      identity_uri          => hiera('CONFIG_KEYSTONE_ADMIN_URL'),
      use_neutron           => ($sahara_cfg_config_neutron_install == 'y'),
      host                  => hiera('CONFIG_SAHARA_HOST'),
      rabbit_use_ssl        => hiera('CONFIG_AMQP_SSL_ENABLED'),
      default_transport_url => "rabbit://${rabbit_userid}:${rabbit_password}@${rabbit_host}:${rabbit_port}/",
      kombu_ssl_ca_certs    => $kombu_ssl_ca_certs,
      kombu_ssl_keyfile     => $kombu_ssl_keyfile,
      kombu_ssl_certfile    => $kombu_ssl_certfile,
    }
}
