class packstack::nova ()
{
    $nova_db_pw = hiera('CONFIG_NOVA_DB_PW')
    $nova_mariadb_host = hiera('CONFIG_MARIADB_HOST_URL')

    $rabbit_host = hiera('CONFIG_AMQP_HOST_URL')
    $rabbit_port = hiera('CONFIG_AMQP_CLIENTS_PORT')
    $rabbit_userid = hiera('CONFIG_AMQP_AUTH_USER')
    $rabbit_password = hiera('CONFIG_AMQP_AUTH_PASSWORD')

    $private_key = {
      'type' => hiera('NOVA_MIGRATION_KEY_TYPE'),
      key  => hiera('NOVA_MIGRATION_KEY_SECRET'),
    }
    $public_key = {
      'type' => hiera('NOVA_MIGRATION_KEY_TYPE'),
      key  => hiera('NOVA_MIGRATION_KEY_PUBLIC'),
    }


    $kombu_ssl_ca_certs = hiera('CONFIG_AMQP_SSL_CACERT_FILE', undef)
    $kombu_ssl_keyfile = hiera('CONFIG_NOVA_SSL_KEY', undef)
    $kombu_ssl_certfile = hiera('CONFIG_NOVA_SSL_CERT', undef)

    if $kombu_ssl_keyfile {
      $files_to_set_owner = [ $kombu_ssl_keyfile, $kombu_ssl_certfile ]
      file { $files_to_set_owner:
        owner   => 'nova',
        group   => 'nova',
        require => Package['nova-common'],
      }
      File[$files_to_set_owner] ~> Service<| tag == 'nova-service' |>
    }

    $nova_common_rabbitmq_cfg_storage_host = hiera('CONFIG_STORAGE_HOST_URL')
    if hiera('CONFIG_CEILOMETER_INSTALL') == 'y' {
      $nova_common_notification_driver = 'messagingv2'
      $notify_on_state_change = 'vm_and_task_state'
    } else {
      $nova_common_notification_driver = undef
      $notify_on_state_change = undef
    }

    if hiera('CONFIG_NEUTRON_L2_AGENT') == 'ovn' {
      $novahost = $::fqdn
    } else {
      $novahost = undef
    }

    class { '::nova':
      glance_api_servers            => "http://${nova_common_rabbitmq_cfg_storage_host}:9292",
      default_transport_url         => "rabbit://${rabbit_userid}:${rabbit_password}@${rabbit_host}:${rabbit_port}/",
      rabbit_use_ssl                => hiera('CONFIG_AMQP_SSL_ENABLED'),
      debug                         => hiera('CONFIG_DEBUG_MODE'),
      nova_public_key               => $public_key,
      nova_private_key              => $private_key,
      kombu_ssl_ca_certs            => $kombu_ssl_ca_certs,
      kombu_ssl_keyfile             => $kombu_ssl_keyfile,
      kombu_ssl_certfile            => $kombu_ssl_certfile,
      notification_driver           => $nova_common_notification_driver,
      notify_on_state_change        => $notify_on_state_change,
      database_connection           => "mysql+pymysql://nova:${nova_db_pw}@${nova_mariadb_host}/nova",
      api_database_connection       => "mysql+pymysql://nova_api:${nova_db_pw}@${nova_mariadb_host}/nova_api",
      placement_database_connection => "mysql+pymysql://nova_placement:${nova_db_pw}@${nova_mariadb_host}/nova_placement",
      cpu_allocation_ratio          => hiera('CONFIG_NOVA_SCHED_CPU_ALLOC_RATIO'),
      ram_allocation_ratio          => hiera('CONFIG_NOVA_SCHED_RAM_ALLOC_RATIO'),
      host                          => $novahost,
    }
}
