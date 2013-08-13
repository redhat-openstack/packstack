package { 'nfs-utils': ensure => present }

class { 'cinder::volume::nfs':
    nfs_servers => [%(CONFIG_CINDER_NFS_MOUNTS)s],
    require => Package['nfs-utils'],
}
