class packstack::swift::storage ()
{
    create_resources(packstack::firewall, lookup('FIREWALL_SWIFT_STORAGE_RULES', undef, undef, {}))

    # install all swift storage servers together
    class { 'swift::storage::all':
      # looks like ipv6 address without brackets is required here
      storage_local_net_ip => lookup('CONFIG_STORAGE_HOST'),
      require              => Class['swift'],
    }

    if (!defined(File['/srv/node'])) {
      file { '/srv/node':
        ensure  => directory,
        owner   => 'swift',
        group   => 'swift',
        require => Package['swift'],
      }
    }

    swift::ringsync{ ['account', 'container', 'object']:
      ring_server => lookup('CONFIG_STORAGE_HOST_URL'),
      before      => Class['swift::storage::all'],
      require     => Class['swift'],
    }

    if lookup('CONFIG_SWIFT_LOOPBACK') == 'y' {
      swift::storage::loopback { 'swiftloopback':
        base_dir     => '/srv/loopback-device',
        mnt_base_dir => '/srv/node',
        require      => Class['swift'],
        fstype       => lookup('CONFIG_SWIFT_STORAGE_FSTYPE'),
        seek         => lookup('CONFIG_SWIFT_STORAGE_SEEK'),
      }
    }
    else {
        create_resources(packstack::swift::fs, lookup('CONFIG_SWIFT_STORAGE_DEVICES', undef, undef, {}))
    }
}
