class packstack::swift::ringbuilder ()
{
    class { '::swift::ringbuilder':
      part_power     => '18',
      replicas       => hiera('CONFIG_SWIFT_STORAGE_REPLICAS'),
      min_part_hours => 1,
      require        => Class['swift'],
    }

    # sets up an rsync db that can be used to sync the ring DB
    class { '::swift::ringserver':
      local_net_ip => hiera('CONFIG_STORAGE_HOST_URL'),
    }

    if str2bool($::selinux) {
      selboolean { 'rsync_export_all_ro':
        value      => on,
        persistent => true,
      }
    }

    create_resources(ring_account_device, hiera('SWIFT_RING_ACCOUNT_DEVICES', {}))
    create_resources(ring_object_device, hiera('SWIFT_RING_OBJECT_DEVICES', {}))
    create_resources(ring_container_device, hiera('SWIFT_RING_CONTAINER_DEVICES', {}))
}
