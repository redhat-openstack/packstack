class packstack::neutron::rabbitmq ()
{
    $bind_host = hiera('CONFIG_IP_VERSION') ? {
      'ipv6'  => '::0',
      default => '0.0.0.0',
      # TO-DO(mmagr): Add IPv6 support when hostnames are used
    }

    $kombu_ssl_ca_certs = hiera('CONFIG_AMQP_SSL_CACERT_FILE', undef)
    $kombu_ssl_keyfile = hiera('CONFIG_NEUTRON_SSL_KEY', undef)
    $kombu_ssl_certfile = hiera('CONFIG_NEUTRON_SSL_CERT', undef)

    $rabbit_host = hiera('CONFIG_AMQP_HOST_URL')
    $rabbit_port = hiera('CONFIG_AMQP_CLIENTS_PORT')
    $rabbit_userid = hiera('CONFIG_AMQP_AUTH_USER')
    $rabbit_password = hiera('CONFIG_AMQP_AUTH_PASSWORD')

    if $kombu_ssl_keyfile {
      $files_to_set_owner = [ $kombu_ssl_keyfile, $kombu_ssl_certfile ]
      file { $files_to_set_owner:
        owner   => 'neutron',
        group   => 'neutron',
        require => Package['neutron'],
      }
      File[$files_to_set_owner] ~> Service<| tag == 'neutron-service' |>
    }


    class { '::neutron':
      bind_host             => $bind_host,
      rabbit_use_ssl        => hiera('CONFIG_AMQP_SSL_ENABLED'),
      default_transport_url => "rabbit://${rabbit_userid}:${rabbit_password}@${rabbit_host}:${rabbit_port}/",
      core_plugin           => hiera('CONFIG_NEUTRON_CORE_PLUGIN'),
      allow_overlapping_ips => true,
      service_plugins       => hiera_array('SERVICE_PLUGINS'),
      debug                 => hiera('CONFIG_DEBUG_MODE'),
      kombu_ssl_ca_certs    => $kombu_ssl_ca_certs,
      kombu_ssl_keyfile     => $kombu_ssl_keyfile,
      kombu_ssl_certfile    => $kombu_ssl_certfile,
    }
}
