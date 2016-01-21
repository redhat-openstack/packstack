package { 'glusterfs-fuse':
  ensure => present,
}

cinder::backend::glusterfs { 'gluster':
  glusterfs_shares        => hiera_array('CONFIG_CINDER_GLUSTER_MOUNTS'),
  require                 => Package['glusterfs-fuse'],
  glusterfs_shares_config => '/etc/cinder/glusterfs_shares.conf',
}

# TO-DO: Remove this workaround as soon as bz#1239040 will be resolved
if $cinder_keystone_api == 'v3' {
  Exec <| title == 'cinder type-create glusterfs' or title == 'cinder type-key glusterfs set volume_backend_name=gluster' |> {
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

cinder::type { 'glusterfs':
  set_key   => 'volume_backend_name',
  set_value => 'gluster',
  require   => Class['cinder::api'],
}
