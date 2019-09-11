class packstack::cinder::backend::nfs ()
{
    ensure_packages(['nfs-utils'], {'ensure' => 'present'})

    cinder::backend::nfs { 'nfs':
      nfs_servers       => hiera_array('CONFIG_CINDER_NFS_MOUNTS'),
      require           => Package['nfs-utils'],
      nfs_shares_config => '/etc/cinder/nfs_shares.conf',
    }

    cinder_type { 'nfs':
      ensure     => present,
      properties => ["volume_backend_name=nfs"],
      require   => Class['cinder::api'],
    }
}
