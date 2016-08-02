$amqp = hiera('CONFIG_AMQP_BACKEND')
$amqp_enable_ssl = hiera('CONFIG_AMQP_SSL_ENABLED')

case $amqp  {
  'rabbitmq': {
    enable_rabbitmq { 'rabbitmq': }
  }
  default: {}
}


define enable_rabbitmq {

  if $::amqp_enable_ssl {
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
      ssl_port                 => hiera('CONFIG_AMQP_CLIENTS_PORT'),
      ssl_only                 => true,
      ssl                      => $::amqp_enable_ssl,
      ssl_cacert               => $kombu_ssl_ca_certs,
      ssl_cert                 => $kombu_ssl_certfile,
      ssl_key                  => $kombu_ssl_keyfile,
      default_user             => hiera('CONFIG_AMQP_AUTH_USER'),
      default_pass             => hiera('CONFIG_AMQP_AUTH_PASSWORD'),
      package_provider         => 'yum',
      repos_ensure             => false,
      admin_enable             => false,
      # FIXME: it's ugly to not to require client certs
      ssl_fail_if_no_peer_cert => true,
      config_variables         => {
        'tcp_listen_options' => '[binary,{packet, raw},{reuseaddr, true},{backlog, 128},{nodelay, true},{exit_on_close, false},{keepalive, true}]',
        'loopback_users'     => '[]',
      },
    }
  } else {
    class { '::rabbitmq':
      port             => hiera('CONFIG_AMQP_CLIENTS_PORT'),
      ssl              => $::amqp_enable_ssl,
      default_user     => hiera('CONFIG_AMQP_AUTH_USER'),
      default_pass     => hiera('CONFIG_AMQP_AUTH_PASSWORD'),
      package_provider => 'yum',
      repos_ensure     => false,
      admin_enable     => false,
      config_variables => {
        'tcp_listen_options' => '[binary,{packet, raw},{reuseaddr, true},{backlog, 128},{nodelay, true},{exit_on_close, false},{keepalive, true}]',
        'loopback_users'     => '[]',
      },
    }
  }

  File <| path == '/etc/rabbitmq/rabbitmq.config' |> {
    ensure  => present,
    owner   => 'rabbitmq',
    group   => 'rabbitmq',
    mode    => '0640',
  }

}
