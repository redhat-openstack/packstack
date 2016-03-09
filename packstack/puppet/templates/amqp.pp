$amqp = hiera('CONFIG_AMQP_BACKEND')
$amqp_enable_ssl = hiera('CONFIG_AMQP_SSL_ENABLED')

case $amqp  {
  'qpid': {
    enable_qpid { 'qpid':
      enable_ssl  => $amqp_enable_ssl,
      enable_auth => hiera('CONFIG_AMQP_ENABLE_AUTH'),
    }
  }
  'rabbitmq': {
    enable_rabbitmq { 'rabbitmq': }
  }
  default: {}
}


define enable_rabbitmq {
  package { 'erlang':
    ensure => 'installed',
  }

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

  Package['erlang'] -> Class['rabbitmq']
}

define enable_qpid($enable_ssl = 'n', $enable_auth = 'n') {
  case $::operatingsystem {
    'Fedora': {
      if (versioncmp($::operatingsystemmajrelease, '20') >= 0) or $::operatingsystemrelease == 'Rawhide' {
        $config = '/etc/qpid/qpidd.conf'
      } else {
        $config = '/etc/qpidd.conf'
      }
    }

    'RedHat', 'CentOS', 'Scientific': {
      if (versioncmp($::operatingsystemmajrelease, '7') >= 0) {
        $config = '/etc/qpid/qpidd.conf'
      } else {
        $config = '/etc/qpidd.conf'
      }
    }

    default: {
      $config = '/etc/qpidd.conf'
    }
  }

  class { '::qpid::server':
    config_file             => $config,
    auth                    => $enable_auth ? {
      'y'     => 'yes',
      default => 'no',
    },
    clustered               => false,
      ssl_port              => hiera('CONFIG_AMQP_CLIENTS_PORT'),
      ssl                   => hiera('CONFIG_AMQP_SSL_ENABLED'),
      ssl_cert              => '/etc/pki/tls/certs/ssl_amqp.crt',
      ssl_key               => '/etc/pki/tls/private/ssl_amqp.key',
      ssl_database_password => hiera('CONFIG_AMQP_NSS_CERTDB_PW', undef),
  }

  if $enable_auth == 'y' {
    add_qpid_user { 'qpid_user': }
  }

}

define add_qpid_user {
  $config_amqp_auth_user = hiera('CONFIG_AMQP_AUTH_USER')
  qpid_user { $config_amqp_auth_user:
    password => hiera('CONFIG_AMQP_AUTH_PASSWORD'),
    file     => '/var/lib/qpidd/qpidd.sasldb',
    realm    => 'QPID',
    provider => 'saslpasswd2',
    require  => Class['qpid::server'],
  }

  file { 'sasldb_file':
    ensure  => file,
    path    => '/var/lib/qpidd/qpidd.sasldb',
    owner   => 'qpidd',
    group   => 'qpidd',
    require => Package['qpid-cpp-server'],
  }
}
