class packstack::cinder::backend::nfs ()
{
    ensure_packages(['nfs-utils'], {'ensure' => 'present'})

    cinder::backend::nfs { 'nfs':
      nfs_servers       => hiera_array('CONFIG_CINDER_NFS_MOUNTS'),
      require           => Package['nfs-utils'],
      nfs_shares_config => '/etc/cinder/nfs_shares.conf',
    }

    cinder::type { 'nfs':
      set_key   => 'volume_backend_name',
      set_value => 'nfs',
      require   => Class['cinder::api'],
    }
}
