$amqp = hiera('CONFIG_AMQP_BACKEND')

case $amqp  {
  'qpid': {
    enable_qpid { 'qpid':
      enable_ssl  => hiera('CONFIG_AMQP_ENABLE_SSL'),
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

  class { 'rabbitmq':
    port                => hiera('CONFIG_AMQP_CLIENTS_PORT'),
    ssl_management_port => hiera('CONFIG_AMQP_SSL_PORT'),
    ssl                 => hiera('CONFIG_AMQP_ENABLE_SSL'),
    ssl_cert            => hiera('CONFIG_AMQP_SSL_CERT_FILE'),
    ssl_key             => hiera('CONFIG_AMQP_SSL_KEY_FILE'),
    default_user        => hiera('CONFIG_AMQP_AUTH_USER'),
    default_pass        => hiera('CONFIG_AMQP_AUTH_PASSWORD'),
    package_provider    => 'yum',
    admin_enable        => false,
    config_variables    => {
        'tcp_listen_options'  => "[binary,{packet, raw},{reuseaddr, true},{backlog, 128},{nodelay, true},{exit_on_close, false},{keepalive, true}]"
    }
  }

  Package['erlang'] -> Class['rabbitmq']
}

define enable_qpid($enable_ssl = 'n', $enable_auth = 'n') {
  case $::operatingsystem {
    'Fedora': {
      if (is_integer($::operatingsystemrelease) and $::operatingsystemrelease >= 20) or $::operatingsystemrelease == 'Rawhide' {
        $config = '/etc/qpid/qpidd.conf'
      } else {
        $config = '/etc/qpidd.conf'
      }
    }

    'RedHat', 'CentOS', 'Scientific': {
      if $::operatingsystemmajrelease >= 7 {
        $config = '/etc/qpid/qpidd.conf'
      } else {
        $config = '/etc/qpidd.conf'
      }
    }

    default: {
      $config = '/etc/qpidd.conf'
    }
  }

  class { 'qpid::server':
    config_file             => $config,
    auth                    => $enable_auth ? {
      'y'     => 'yes',
      default => 'no',
      },
    clustered               => false,
      ssl_port              => hiera('CONFIG_AMQP_SSL_PORT'),
      ssl                   => hiera('CONFIG_AMQP_ENABLE_SSL'),
      ssl_cert              => hiera('CONFIG_AMQP_SSL_CERT_FILE'),
      ssl_key               => hiera('CONFIG_AMQP_SSL_KEY_FILE'),
      ssl_database_password => hiera('CONFIG_AMQP_NSS_CERTDB_PW'),
  }

  if $enable_ssl {
    # If there is qpid-cpp-server-ssl install it
    exec { 'install_qpid_ssl':
      path    => '/usr/bin',
      command => 'yum install -y -d 0 -e 0  qpid-cpp-server-ssl',
      onlyif  => 'yum info qpid-cpp-server-ssl',
      before  => Service['qpidd'],
      require => Package['qpid-cpp-server'],
    }
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

