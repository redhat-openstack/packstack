
# install all swift storage servers together
class { 'swift::storage::all':
  storage_local_net_ip => hiera('CONFIG_CONTROLLER_HOST'),
  allow_versions       => true,
  require              => Class['swift'],
}

if (!defined(File['/srv/node'])) {
  file { '/srv/node':
    ensure  => directory,
    owner   => 'swift',
    group   => 'swift',
    require => Package['openstack-swift'],
  }
}

swift::ringsync{ ['account', 'container', 'object']:
  ring_server => hiera('CONFIG_CONTROLLER_HOST'),
  before      => Class['swift::storage::all'],
  require     => Class['swift'],
}
