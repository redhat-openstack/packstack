define enable_rabbitmq {
  create_resources(packstack::firewall, hiera('FIREWALL_AMQP_RULES', {}))
  $amqp_enable_ssl = hiera('CONFIG_AMQP_SSL_ENABLED')

  if $amqp_enable_ssl {
    $kombu_ssl_ca_certs = hiera('CONFIG_AMQP_SSL_CACERT_FILE', undef)
    $kombu_ssl_keyfile = '/etc/pki/tls/private/ssl_amqp.key'
    $kombu_ssl_certfile = '/etc/pki/tls/certs/ssl_amqp.crt'

    $files_to_set_owner = [ $kombu_ssl_keyfile, $kombu_ssl_certfile ]
    file { $files_to_set_owner:
      owner   => 'rabbitmq',
      group   => 'rabbitmq',
      require => Package['rabbitmq-server'],
      notify  => Service['rabbitmq-server'],
    }

    class { '::rabbitmq':
      port                     => undef,
      ssl_port                 => 0 + hiera('CONFIG_AMQP_CLIENTS_PORT'),
      ssl_only                 => true,
      ssl                      => true,
      ssl_cacert               => $kombu_ssl_ca_certs,
      ssl_cert                 => $kombu_ssl_certfile,
      ssl_key                  => $kombu_ssl_keyfile,
      default_user             => hiera('CONFIG_AMQP_AUTH_USER'),
      default_pass             => hiera('CONFIG_AMQP_AUTH_PASSWORD'),
      package_provider         => 'yum',
      repos_ensure             => false,
      admin_enable             => false,
      loopback_users           => [],
      # FIXME: it's ugly to not to require client certs
      ssl_fail_if_no_peer_cert => true,
      config_variables         => {
     'tcp_listen_options' => '[binary,{packet, raw},{reuseaddr, true},{backlog, 128},{nodelay, true},{exit_on_close, false},{keepalive, true}]',
      },
    }
  } else {
    class { '::rabbitmq':
      port             => 0 + hiera('CONFIG_AMQP_CLIENTS_PORT'),
      ssl              => false,
      default_user     => hiera('CONFIG_AMQP_AUTH_USER'),
      default_pass     => hiera('CONFIG_AMQP_AUTH_PASSWORD'),
      package_provider => 'yum',
      repos_ensure     => false,
      admin_enable     => false,
      loopback_users   => [],
      config_variables => {
     'tcp_listen_options' => '[binary,{packet, raw},{reuseaddr, true},{backlog, 128},{nodelay, true},{exit_on_close, false},{keepalive, true}]',
      },
    }
  }
}

class packstack::amqp ()
{
     $amqp = hiera('CONFIG_AMQP_BACKEND')

     case $amqp  {
       'rabbitmq': {
         enable_rabbitmq { 'rabbitmq': }

          # The following kernel parameters help alleviate some RabbitMQ
          # connection issues

          sysctl::value { 'net.ipv4.tcp_keepalive_intvl':
            value => '1',
          }

          sysctl::value { 'net.ipv4.tcp_keepalive_probes':
            value => '5',
          }

          sysctl::value { 'net.ipv4.tcp_keepalive_time':
            value => '5',
          }
       }
       default: {}
     }
}
