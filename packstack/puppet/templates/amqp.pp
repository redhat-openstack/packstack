$amqp = '%(CONFIG_AMQP_SERVER)s'
case $amqp  {
  'qpid': {
    enable_qpid {"qpid":
      enable_ssl  => %(CONFIG_AMQP_ENABLE_SSL)s,
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

  class {"rabbitmq":
    port             => '%(CONFIG_AMQP_CLIENTS_PORT)s',
    ssl_management_port      => '%(CONFIG_AMQP_SSL_PORT)s',
    ssl              => %(CONFIG_AMQP_ENABLE_SSL)s,
    ssl_cert         => '%(CONFIG_AMQP_SSL_CERT_FILE)s',
    ssl_key          => '%(CONFIG_AMQP_SSL_KEY_FILE)s',
    default_user     => '%(CONFIG_AMQP_AUTH_USER)s',
    default_pass     => '%(CONFIG_AMQP_AUTH_PASSWORD)s',
    package_provider => 'yum',
    admin_enable     => false,
  }

  Package['erlang']->Class['rabbitmq']
}

define enable_qpid($enable_ssl = 'n', $enable_auth = 'n') {

  class {"qpid::server":
	  config_file => $::operatingsystem? {
	    'Fedora' => '/etc/qpid/qpidd.conf',
	    default  => '/etc/qpidd.conf',
	    },
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
    enable_qpid_ssl {"qpid":}
  }
  if $enable_auth == 'y' {
    add_qpid_user {"qpid_user":}
  }

}

define enable_qpid_ssl {
  # User and group for the nss database
  group { 'qpidd':
    ensure => 'present',
  }

  exec { 'stop_qpid' :
    command => '/sbin/service qpidd stop',
    onlyif  => '/sbin/service qpidd status',
  }

  user { 'qpidd':
    ensure     => 'present',
    managehome => true,
    home       => '/var/run/qpidd',
    gid        => 'qpidd',
    before     => Class['qpid::server']
  }

  Exec['stop_qpid']->User['qpidd']

  file { 'pid_dir':
    path => '/var/run/qpidd',
    ensure => directory,
    owner => 'qpidd',
    group => 'qpidd',
    require => User['qpidd'],
  }

  file_line { 'pid_dir_conf':
    path => $qpid::server::config_file,
    line => 'pid-dir=/var/run/qpidd',
    require => File['pid_dir'],
  }
}

define add_qpid_user {
  qpid_user { '%(CONFIG_AMQP_AUTH_USER)s':
    password  => '%(CONFIG_AMQP_AUTH_PASSWORD)s',
    file  => '/var/lib/qpidd/qpidd.sasldb',
    realm  => 'AMQP',
    provider => 'saslpasswd2',
    require   => Class['qpid::server'],
  }

  file { 'sasldb_file':
    path => '/var/lib/qpidd/qpidd.sasldb',
    ensure => file,
    owner => 'qpidd',
    group => 'qpidd',
  }
}
