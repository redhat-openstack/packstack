package { 'glusterfs-fuse': ensure => present }

class { 'cinder::volume::glusterfs':
    glusterfs_shares => [%(CONFIG_CINDER_GLUSTER_MOUNTS)s],
    require => Package['glusterfs-fuse'],
}
