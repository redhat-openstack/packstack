cinder::backend::vmdk { 'vmdk':
  host_ip       => hiera('CONFIG_VCENTER_HOST'),
  host_username => hiera('CONFIG_VCENTER_USER'),
  host_password => hiera('CONFIG_VCENTER_PASSWORD'),
}

# TO-DO: Remove this workaround as soon as bz#1239040 will be resolved
if $cinder_keystone_api == 'v3' {
  Exec <| title == 'cinder type-create vmdk' or title == 'cinder type-key vmdk set volume_backend_name=vmdk' |> {
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

cinder::type { 'vmdk':
  set_key   => 'volume_backend_name',
  set_value => 'vmdk',
  require   => Class['cinder::api'],
}
