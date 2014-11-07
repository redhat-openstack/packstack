
swift::storage::loopback { 'swiftloopback':
  base_dir     => '/srv/loopback-device',
  mnt_base_dir => '/srv/node',
  require      => Class['swift'],
  fstype       => hiera('CONFIG_SWIFT_STORAGE_FSTYPE'),
  seek         => hiera('CONFIG_SWIFT_STORAGE_SEEK'),
}


