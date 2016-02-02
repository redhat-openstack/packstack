ironic_config {
  'glance/glance_host': value => hiera('CONFIG_STORAGE_HOST_URL');
}

class { '::ironic::api':
  identity_uri   => hiera('CONFIG_KEYSTONE_ADMIN_URL'),
  auth_uri       => hiera('CONFIG_KEYSTONE_PUBLIC_URL'),
  admin_password => hiera('CONFIG_IRONIC_KS_PW'),
}

# TO-DO: Remove this workaround as soon as module support is implemented (see rhbz#1300662)
ironic_config {
  'keystone_authtoken/auth_version': value => hiera('CONFIG_KEYSTONE_API_VERSION');
}

class { '::ironic::client': }

class { '::ironic::conductor': }
