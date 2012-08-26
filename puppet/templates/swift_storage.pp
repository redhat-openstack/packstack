

swift::storage::loopback { [%(SWIFT_STORAGE_DEVICES)s]:
  base_dir     => '/srv/loopback-device',
  mnt_base_dir => '/srv/node',
  require      => Class['swift'],
  fstype       => '%(CONFIG_SWIFT_STORAGE_FSTYPE)s',
}

# install all swift storage servers together
class { 'swift::storage::all':
  storage_local_net_ip => '%(CONFIG_SWIFT_STORAGE_CURRENT)s',
  require => Class['swift'],
}

swift::ringsync{["account","container","object"]:
    ring_server => '%(CONFIG_SWIFT_BUILDER_HOST)s',
    notify => Class['swift::storage::all']
}

firewall { '001 swift storage incomming':
    proto    => 'tcp',
    dport    => ['6000', '6001', '6002', '873'],
    action   => 'accept',
}


