package { 'nfs-utils': ensure => present }

cinder::backend::nfs { 'nfs':
  nfs_servers       => hiera_array('CONFIG_CINDER_NFS_MOUNTS'),
  require           => Package['nfs-utils'],
  nfs_shares_config => '/etc/cinder/nfs_shares.conf',
}

# TO-DO: Remove this workaround as soon as bz#1239040 will be resolved
if $cinder_keystone_api == 'v3' {
  Exec <| title == 'cinder type-create nfs' or title == 'cinder type-key nfs set volume_backend_name=nfs' |> {
    environment => [
      "OS_USERNAME=${cinder_keystone_admin_username}",
      "OS_PASSWORD=${cinder_keystone_admin_password}",
      "OS_AUTH_URL=${cinder_keystone_auth_url}",
      "OS_IDENTITY_API_VERSION=${cinder_keystone_api}",
      "OS_PROJECT_NAME=admin",
      "OS_USER_DOMAIN_NAME=Default",
      "OS_PROJECT_DOMAIN_NAME=Default",
    ],
  }
}

cinder::type { 'nfs':
  set_key   => 'volume_backend_name',
  set_value => 'nfs',
  require   => Class['cinder::api'],
}
