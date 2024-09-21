class packstack::nova ()
{
    $nova_db_pw = lookup('CONFIG_NOVA_DB_PW')
    $nova_mariadb_host = lookup('CONFIG_MARIADB_HOST_URL')

    $rabbit_host = lookup('CONFIG_AMQP_HOST_URL')
    $rabbit_port = lookup('CONFIG_AMQP_CLIENTS_PORT')
    $rabbit_userid = lookup('CONFIG_AMQP_AUTH_USER')
    $rabbit_password = lookup('CONFIG_AMQP_AUTH_PASSWORD')

    $private_key = {
      'type' => lookup('NOVA_MIGRATION_KEY_TYPE'),
      key  => lookup('NOVA_MIGRATION_KEY_SECRET'),
    }
    $public_key = {
      'type' => lookup('NOVA_MIGRATION_KEY_TYPE'),
      key  => lookup('NOVA_MIGRATION_KEY_PUBLIC'),
    }


    $kombu_ssl_ca_certs = lookup('CONFIG_AMQP_SSL_CACERT_FILE', undef, undef, undef)
    $kombu_ssl_keyfile = lookup('CONFIG_NOVA_SSL_KEY', undef, undef, undef)
    $kombu_ssl_certfile = lookup('CONFIG_NOVA_SSL_CERT', undef, undef, undef)

    if $kombu_ssl_keyfile {
      $files_to_set_owner = [ $kombu_ssl_keyfile, $kombu_ssl_certfile ]
      file { $files_to_set_owner:
        owner   => 'nova',
        group   => 'nova',
        require => Package['nova-common'],
      }
      File[$files_to_set_owner] ~> Service<| tag == 'nova-service' |>
    }
    Service<| name == 'rabbitmq-server' |> -> Service<| tag == 'nova-service' |>

    if lookup('CONFIG_CEILOMETER_INSTALL') == 'y' {
      $nova_common_notification_driver = 'messagingv2'
      $notify_on_state_change = 'vm_and_task_state'
    } else {
      $nova_common_notification_driver = undef
      $notify_on_state_change = undef
    }

    if lookup('CONFIG_NEUTRON_L2_AGENT') == 'ovn' {
      $novahost = $facts['networking']['fqdn']
    } else {
      $novahost = undef
    }

    if lookup('CONFIG_HORIZON_SSL') == 'y' {
      $ssl_only = true
      $cert = lookup('CONFIG_VNC_SSL_CERT')
      $key = lookup('CONFIG_VNC_SSL_KEY')
    } else {
      $ssl_only = false
      $cert = undef
      $key = undef
    }

    class { 'nova::logging':
      debug => lookup('CONFIG_DEBUG_MODE'),
    }

    class { 'nova::db':
      database_connection     => "mysql+pymysql://nova:${nova_db_pw}@${nova_mariadb_host}/nova",
      api_database_connection => "mysql+pymysql://nova_api:${nova_db_pw}@${nova_mariadb_host}/nova_api",
    }

    class { 'nova':
      default_transport_url   => "rabbit://${rabbit_userid}:${rabbit_password}@${rabbit_host}:${rabbit_port}/",
      rabbit_use_ssl          => lookup('CONFIG_AMQP_SSL_ENABLED'),
      nova_public_key         => $public_key,
      nova_private_key        => $private_key,
      kombu_ssl_ca_certs      => $kombu_ssl_ca_certs,
      kombu_ssl_keyfile       => $kombu_ssl_keyfile,
      kombu_ssl_certfile      => $kombu_ssl_certfile,
      notification_driver     => $nova_common_notification_driver,
      notify_on_state_change  => $notify_on_state_change,
      cpu_allocation_ratio    => lookup('CONFIG_NOVA_SCHED_CPU_ALLOC_RATIO'),
      ram_allocation_ratio    => lookup('CONFIG_NOVA_SCHED_RAM_ALLOC_RATIO'),
      host                    => $novahost,
      ssl_only                => $ssl_only,
      cert                    => $cert,
      key                     => $key,
    }

    class { 'nova::keystone::service_user':
      send_service_user_token => true,
      password                => lookup('CONFIG_NOVA_KS_PW'),
      auth_url                => lookup('CONFIG_KEYSTONE_ADMIN_URL'),
    }

}
