class packstack::cinder::backend::gluster ()
{
    ensure_packages(['glusterfs-fuse'], {'ensure' => 'present'})

    cinder::backend::glusterfs { 'gluster':
      glusterfs_shares        => hiera_array('CONFIG_CINDER_GLUSTER_MOUNTS'),
      require                 => Package['glusterfs-fuse'],
      glusterfs_shares_config => '/etc/cinder/glusterfs_shares.conf',
    }

    cinder::type { 'glusterfs':
      set_key   => 'volume_backend_name',
      set_value => 'gluster',
      require   => Class['cinder::api'],
    }
}
