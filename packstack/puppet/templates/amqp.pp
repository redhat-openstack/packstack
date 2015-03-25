$amqp_enable_ssl = %(CONFIG_AMQP_ENABLE_SSL)s
$amqp = '%(CONFIG_AMQP_BACKEND)s'
case $amqp  {
  'qpid': {
    enable_qpid {"qpid":
      enable_ssl  => $amqp_enable_ssl,
      enable_auth => '%(CONFIG_AMQP_ENABLE_AUTH)s',
    }
  }
  'rabbitmq': {
    enable_rabbitmq {"rabbitmq":}

  }
}


define enable_rabbitmq {
  package { "erlang":
    ensure => "installed"
  }

  if $amqp_enable_ssl {

    $kombu_ssl_ca_certs ='%(CONFIG_AMQP_SSL_CACERT_FILE)s'
    $kombu_ssl_keyfile = '%(CONFIG_AMQP_SSL_KEY_FILE)s'
    $kombu_ssl_certfile ='%(CONFIG_AMQP_SSL_CERT_FILE)s'

    $files_to_set_owner = [ $kombu_ssl_keyfile, $kombu_ssl_certfile ]
    file { $files_to_set_owner:
      owner   => 'rabbitmq',
      group   => 'rabbitmq',
      require => Package['rabbitmq-server'],
      notify  => Service['rabbitmq-server'],
    }

    class {"rabbitmq":
      ssl                      => $amqp_enable_ssl,
      ssl_cacert               => $kombu_ssl_ca_certs,
      ssl_cert                 => $kombu_ssl_certfile,
      ssl_key                  => $kombu_ssl_keyfile,
      default_user             => '%(CONFIG_AMQP_AUTH_USER)s',
      default_pass             => '%(CONFIG_AMQP_AUTH_PASSWORD)s',
      package_provider         => 'yum',
      admin_enable             => false,
      # FIXME: it's ugly to not to require client certs
      ssl_fail_if_no_peer_cert => false,
      config_variables         => {
        'tcp_listen_options' => "[binary,{packet, raw},{reuseaddr, true},{backlog, 128},{nodelay, true},{exit_on_close, false},{keepalive, true}]",
        'loopback_users'     => "[]",
      }
    }
  } else {
    class {"rabbitmq":
      port             => '%(CONFIG_AMQP_CLIENTS_PORT)s',
      ssl              => $amqp_enable_ssl,
      default_user     => '%(CONFIG_AMQP_AUTH_USER)s',
      default_pass     => '%(CONFIG_AMQP_AUTH_PASSWORD)s',
      package_provider => 'yum',
      admin_enable     => false,
      config_variables => {
        'tcp_listen_options' => "[binary,{packet, raw},{reuseaddr, true},{backlog, 128},{nodelay, true},{exit_on_close, false},{keepalive, true}]",
        'loopback_users'     => "[]",
      }
    }
  }

  Package['erlang']->Class['rabbitmq']
}

define enable_qpid($enable_ssl = 'n', $enable_auth = 'n') {
  case $::operatingsystem {
    'Fedora': {
      if (is_integer($::operatingsystemrelease) and $::operatingsystemrelease >= 20) or $::operatingsystemrelease == "Rawhide" {
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

  class {"qpid::server":
    config_file => $config,
    auth => $enable_auth ? {
	    'y'  => 'yes',
	    default => 'no',
	    },
    clustered => false,
	    ssl_port      => '%(CONFIG_AMQP_SSL_PORT)s',
	    ssl           => %(CONFIG_AMQP_ENABLE_SSL)s,
	    ssl_cert      => '%(CONFIG_AMQP_SSL_CERT_FILE)s',
	    ssl_key       => '%(CONFIG_AMQP_SSL_KEY_FILE)s',
	    ssl_database_password => '%(CONFIG_AMQP_NSS_CERTDB_PW)s',
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
    add_qpid_user {"qpid_user":}
  }

}

define add_qpid_user {
  qpid_user { '%(CONFIG_AMQP_AUTH_USER)s':
    password  => '%(CONFIG_AMQP_AUTH_PASSWORD)s',
    file      => '/var/lib/qpidd/qpidd.sasldb',
    realm     => 'QPID',
    provider  => 'saslpasswd2',
    require   => Class['qpid::server'],
  }

  file { 'sasldb_file':
    path => '/var/lib/qpidd/qpidd.sasldb',
    ensure => file,
    owner => 'qpidd',
    group => 'qpidd',
    require => Package['qpid-cpp-server'],
  }
}
