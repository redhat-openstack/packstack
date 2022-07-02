define packstack::amqp::enable_rabbitmq {
  create_resources(packstack::firewall, lookup('FIREWALL_AMQP_RULES', undef, undef, {}))
  $amqp_enable_ssl = lookup('CONFIG_AMQP_SSL_ENABLED')

  if $amqp_enable_ssl {
    $kombu_ssl_ca_certs = lookup('CONFIG_AMQP_SSL_CACERT_FILE', undef, undef, undef)
    $kombu_ssl_keyfile = '/etc/pki/tls/private/ssl_amqp.key'
    $kombu_ssl_certfile = '/etc/pki/tls/certs/ssl_amqp.crt'

    $files_to_set_owner = [ $kombu_ssl_keyfile, $kombu_ssl_certfile ]
    file { $files_to_set_owner:
      owner   => 'rabbitmq',
      group   => 'rabbitmq',
      require => Package['rabbitmq-server'],
      notify  => Service['rabbitmq-server'],
    }

    file { $kombu_ssl_ca_certs:
      mode    => '0644',
      require => Package['rabbitmq-server'],
      notify  => Service['rabbitmq-server'],
    }

    class { 'rabbitmq':
      port                     => undef,
      ssl_port                 => 0 + lookup('CONFIG_AMQP_CLIENTS_PORT'),
      ssl_only                 => true,
      ssl                      => true,
      ssl_cacert               => $kombu_ssl_ca_certs,
      ssl_cert                 => $kombu_ssl_certfile,
      ssl_key                  => $kombu_ssl_keyfile,
      default_user             => lookup('CONFIG_AMQP_AUTH_USER'),
      default_pass             => lookup('CONFIG_AMQP_AUTH_PASSWORD'),
      package_provider         => 'yum',
      repos_ensure             => false,
      admin_enable             => false,
      loopback_users           => [],
      ssl_verify               => 'verify_peer',
      ssl_fail_if_no_peer_cert => true,
      config_ranch             => false,
      tcp_keepalive            => true,
      tcp_backlog              => 128,
    }
  } else {
    class { 'rabbitmq':
      port             => 0 + lookup('CONFIG_AMQP_CLIENTS_PORT'),
      ssl              => false,
      default_user     => lookup('CONFIG_AMQP_AUTH_USER'),
      default_pass     => lookup('CONFIG_AMQP_AUTH_PASSWORD'),
      package_provider => 'yum',
      repos_ensure     => false,
      admin_enable     => false,
      loopback_users   => [],
      config_ranch     => false,
      tcp_keepalive    => true,
      tcp_backlog      => 128,
    }
  }
}
