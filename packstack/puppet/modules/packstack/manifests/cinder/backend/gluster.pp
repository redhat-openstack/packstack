class packstack::cinder::backend::gluster ()
{
    ensure_packages(['glusterfs-fuse'], {'ensure' => 'present'})

    cinder::backend::glusterfs { 'gluster':
      glusterfs_shares        => hiera_array('CONFIG_CINDER_GLUSTER_MOUNTS'),
      require                 => Package['glusterfs-fuse'],
      glusterfs_shares_config => '/etc/cinder/glusterfs_shares.conf',
    }

    cinder_type { 'glusterfs':
      ensure     => present,
      properties => ["volume_backend_name=gluster"],
      require    => Class['cinder::api'],
    }
}
