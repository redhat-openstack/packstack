
swift::storage::loopback { [%(SWIFT_STORAGE_DEVICES)s]:
  base_dir     => '/srv/loopback-device',
  mnt_base_dir => '/srv/node',
  require      => Class['swift'],
  fstype       => '%(CONFIG_SWIFT_STORAGE_FSTYPE)s',
  seek         => '%(SWIFT_STORAGE_SEEK)s',
}


