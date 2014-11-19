include packstack::apache_common

$horizon_packages = ['python-memcached', 'python-netaddr']

package { $horizon_packages:
  ensure => present,
  notify => Class['horizon'],
}

$is_django_debug = hiera('CONFIG_DEBUG_MODE') ? {
  true  => 'True',
  false => 'False',
}

class {'horizon':
  secret_key            => hiera('CONFIG_HORIZON_SECRET_KEY'),
  keystone_host         => hiera('CONFIG_CONTROLLER_HOST'),
  keystone_default_role => '_member_',
  # fqdn => [hiera('CONFIG_CONTROLLER_HOST'), "$::fqdn", 'localhost'],
  # TO-DO: Parameter fqdn is used both for ALLOWED_HOSTS in settings_local.py
  # and for ServerAlias directives in vhost.conf which is breaking server
  # accessibility. We need ALLOWED_HOSTS values, but we have to avoid
  # ServerAlias definitions. For now we will use this wildcard hack until
  # puppet-horizon will have separate parameter for each config.
  fqdn                 => '*',
  can_set_mount_point  => 'False',
  compress_offline     => false,
  django_debug         => $is_django_debug,
  file_upload_temp_dir => '/var/tmp',
  listen_ssl           => hiera('CONFIG_HORIZON_SSL'),
  horizon_cert         => '/etc/pki/tls/certs/ssl_ps_server.crt',
  horizon_key          => '/etc/pki/tls/private/ssl_ps_server.key',
  horizon_ca           => '/etc/pki/tls/certs/ssl_ps_chain.crt',
  neutron_options      => {
    'enable_lb'        => hiera('CONFIG_HORIZON_NEUTRON_LB'),
    'enable_firewall'  => hiera('CONFIG_HORIZON_NEUTRON_FW'),
  },
}

$is_horizon_ssl = hiera('CONFIG_HORIZON_SSL')

if $is_horizon_ssl == true {
  file {'/etc/pki/tls/certs/ps_generate_ssl_certs.ssh':
    ensure  => present,
    content => template('packstack/ssl/generate_ssl_certs.sh.erb'),
    mode    => '0755',
  }

  exec {'/etc/pki/tls/certs/ps_generate_ssl_certs.ssh':
    require => File['/etc/pki/tls/certs/ps_generate_ssl_certs.ssh'],
    notify  => Service['httpd'],
    before  => Class['horizon'],
  } ->
  exec { 'nova-novncproxy-restart':
    # ps_generate_ssl_certs.ssh is generating ssl certs for nova-novncproxy
    # so openstack-nova-novncproxy should be restarted.
    path      => ['/sbin', '/usr/sbin', '/bin', '/usr/bin'],
    command   => 'systemctl restart openstack-nova-novncproxy.service',
    logoutput => 'on_failure',
  }

  apache::listen { '443': }

  # little bit of hatred as we'll have to patch upstream puppet-horizon
  file_line {'horizon_ssl_wsgi_fix':
    path    => '/etc/httpd/conf.d/15-horizon_ssl_vhost.conf',
    match   => 'WSGIProcessGroup.*',
    line    => '  WSGIProcessGroup horizon-ssl',
    require => File['15-horizon_ssl_vhost.conf'],
    notify  => Service['httpd'],
  }
}

class { 'memcached': }

$firewall_port = hiera('CONFIG_HORIZON_PORT')

firewall { "001 horizon ${firewall_port}  incoming":
  proto  => 'tcp',
  dport  => [$firewall_port],
  action => 'accept',
}

if ($::selinux != false) {
  selboolean{ 'httpd_can_network_connect':
    value      => on,
    persistent => true,
  }
}
