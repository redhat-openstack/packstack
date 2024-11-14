class packstack::neutron::rabbitmq ()
{
    $bind_host = lookup('CONFIG_IP_VERSION') ? {
      'ipv6'  => '::0',
      default => '0.0.0.0',
      # TO-DO(mmagr): Add IPv6 support when hostnames are used
    }

    $kombu_ssl_ca_certs = lookup('CONFIG_AMQP_SSL_CACERT_FILE', undef, undef, undef)
    $kombu_ssl_keyfile = lookup('CONFIG_NEUTRON_SSL_KEY', undef, undef, undef)
    $kombu_ssl_certfile = lookup('CONFIG_NEUTRON_SSL_CERT', undef, undef, undef)

    if $kombu_ssl_keyfile {
      $files_to_set_owner = [ $kombu_ssl_keyfile, $kombu_ssl_certfile ]
      file { $files_to_set_owner:
        owner   => 'neutron',
        group   => 'neutron',
        require => Package['neutron'],
      }
      File[$files_to_set_owner] ~> Service<| tag == 'neutron-service' |>
    }
    Service<| name == 'rabbitmq-server' |> -> Service<| tag == 'neutron-service' |>

    class { 'neutron::logging':
      debug => lookup('CONFIG_DEBUG_MODE'),
    }

    class { 'neutron':
      bind_host             => $bind_host,
      rabbit_use_ssl        => lookup('CONFIG_AMQP_SSL_ENABLED'),
      default_transport_url => os_transport_url({
        'transport' => 'rabbit',
        'host'      => lookup('CONFIG_AMQP_HOST_URL'),
        'port'      => lookup('CONFIG_AMQP_CLIENTS_PORT'),
        'username'  => lookup('CONFIG_AMQP_AUTH_USER'),
        'password'  => lookup('CONFIG_AMQP_AUTH_PASSWORD')
      }),
      core_plugin           => lookup('CONFIG_NEUTRON_CORE_PLUGIN'),
      service_plugins       => lookup('SERVICE_PLUGINS', { merge => 'unique' }),
      kombu_ssl_ca_certs    => $kombu_ssl_ca_certs,
      kombu_ssl_keyfile     => $kombu_ssl_keyfile,
      kombu_ssl_certfile    => $kombu_ssl_certfile,
    }
}
