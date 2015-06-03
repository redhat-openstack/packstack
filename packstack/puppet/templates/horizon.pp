$horizon_packages = ['python-memcached', 'python-netaddr']

package { $horizon_packages:
  ensure => present,
  notify => Class['horizon'],
}

$is_django_debug = hiera('CONFIG_DEBUG_MODE') ? {
  true  => 'True',
  false => 'False',
}

$bind_host = hiera('CONFIG_IP_VERSION') ? {
  'ipv6' => '::0',
  'ipv4' => '0.0.0.0',
}

$horizon_ssl = hiera('CONFIG_HORIZON_SSL') ? {
  'y' => true,
  'n' => false,
}

class { '::apache':
  purge_configs => false,
}

class {'::horizon':
  secret_key            => hiera('CONFIG_HORIZON_SECRET_KEY'),
  keystone_url          => hiera('CONFIG_KEYSTONE_PUBLIC_URL'),
  keystone_default_role => '_member_',
  server_aliases        => [hiera('CONFIG_CONTROLLER_HOST'), $::fqdn, 'localhost'],
  allowed_hosts         => '*',
  hypervisor_options    => {'can_set_mount_point' => false, },
  compress_offline      => false,
  django_debug          => $is_django_debug,
  file_upload_temp_dir  => '/var/tmp',
  listen_ssl            => $horizon_ssl,
  horizon_cert          => hiera('CONFIG_HORIZON_SSL_CERT', undef),
  horizon_key           => hiera('CONFIG_HORIZON_SSL_KEY', undef),
  horizon_ca            => hiera('CONFIG_HORIZON_SSL_CACERT', undef),
  neutron_options       => {
    'enable_lb'       => hiera('CONFIG_HORIZON_NEUTRON_LB'),
    'enable_firewall' => hiera('CONFIG_HORIZON_NEUTRON_FW'),
  },
}

if $horizon_ssl {
  apache::listen { '443': }
}

if hiera('CONFIG_KEYSTONE_SERVICE_NAME') == 'httpd' {
  apache::listen { '5000': }
  apache::listen { '35357': }
}

# hack for memcached, for now we bind to localhost on ipv6
# https://bugzilla.redhat.com/show_bug.cgi?id=1210658
$memcached_bind_host = hiera('CONFIG_IP_VERSION') ? {
  'ipv6' => 'localhost6',
  'ipv4' => '0.0.0.0',
}

class { '::memcached':
  listen_ip  => $memcached_bind_host,
  max_memory => '10%%',
}

$firewall_port = hiera('CONFIG_HORIZON_PORT')

firewall { "001 horizon ${firewall_port}  incoming":
  proto  => 'tcp',
  dport  => [$firewall_port],
  action => 'accept',
}

if str2bool($::selinux) {
  selboolean{ 'httpd_can_network_connect':
    value      => on,
    persistent => true,
  }
}
