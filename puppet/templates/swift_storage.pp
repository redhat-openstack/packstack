
include role_swift_storage

class role_swift_storage {

  swift::storage::loopback { ['1']:
    base_dir     => '/srv/loopback-device',
    mnt_base_dir => '/srv/node',
    require      => Class['swift'],
    fstype       => '%(CONFIG_SWIFT_STORAGE_FSTYPE)s',
  }

  # install all swift storage servers together
  class { 'swift::storage::all':
    storage_local_net_ip => '%(CONFIG_SWIFT_STORAGE_CURRENT)s',
  }

  # collect resources for synchronizing the ring databases
  Swift::Ringsync<<||>>

}

