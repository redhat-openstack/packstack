package { 'nfs-utils': ensure => present }

cinder::backend::nfs { 'nfs':
  nfs_servers       => [%(CONFIG_CINDER_NFS_MOUNTS)s],
  require           => Package['nfs-utils'],
  nfs_shares_config => '/etc/cinder/nfs_shares.conf',
}

cinder::type { 'nfs':
  set_key   => 'volume_backend_name',
  set_value => 'nfs',
  require   => Class['cinder::api'],
}
