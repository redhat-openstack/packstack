
# install all swift storage servers together
class { 'swift::storage::all':
  storage_local_net_ip => '%(CONFIG_SWIFT_STORAGE_CURRENT)s',
  allow_versions => true,
  require => Class['swift'],
}

if(!defined(File['/srv/node'])) {
  file { '/srv/node':
    owner  => 'swift',
    group  => 'swift',
    ensure => directory,
    require => Package['openstack-swift'],
  }
}

swift::ringsync{["account","container","object"]:
    ring_server => '%(CONFIG_SWIFT_BUILDER_HOST)s',
    before => Class['swift::storage::all'],
    require => Class['swift'],
}


