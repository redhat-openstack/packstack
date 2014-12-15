
package{ 'python-cinderclient':
  before => Class['nova']
}

# Install the private key to be used for live migration.  This needs to be
# configured into libvirt/live_migration_uri in nova.conf.
file { '/etc/nova/ssh':
  ensure => directory,
  owner  => root,
  group  => root,
  mode   => '0700',
}

file { '/etc/nova/ssh/nova_migration_key':
  content => hiera('NOVA_MIGRATION_KEY_SECRET'),
  mode    => '0600',
  owner   => root,
  group   => root,
  require => File['/etc/nova/ssh'],
}

nova_config{
  'DEFAULT/volume_api_class':
    value => 'nova.volume.cinder.API';
  'libvirt/live_migration_uri':
    value => hiera('CONFIG_NOVA_COMPUTE_MIGRATE_URL');
}

$config_horizon_ssl = hiera('CONFIG_HORIZON_SSL')

$vncproxy_proto = $config_horizon_ssl ? {
  true    => 'https',
  false   => 'http',
  default => 'http',
}

class { 'nova::compute':
  enabled                       => true,
  vncproxy_host                 => hiera('CONFIG_CONTROLLER_HOST'),
  vncproxy_protocol             => $vncproxy_proto,
  vncserver_proxyclient_address => hiera('CONFIG_NOVA_COMPUTE_HOST'),
}

# Tune the host with a virtual hosts profile
package { 'tuned':
  ensure => present,
}

service { 'tuned':
  ensure  => running,
  require => Package['tuned'],
}

exec { 'tuned-virtual-host':
  unless  => '/usr/sbin/tuned-adm active | /bin/grep virtual-host',
  command => '/usr/sbin/tuned-adm profile virtual-host',
  require => Service['tuned'],
}


