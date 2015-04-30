cinder_config {
  'DEFAULT/glance_host': value => hiera('CONFIG_STORAGE_HOST_URL');
}

package { 'python-keystone':
  notify => Class['cinder::api'],
}

$bind_host = hiera('CONFIG_IP_VERSION') ? {
  'ipv6' => '::0',
  'ipv4' => '0.0.0.0',
}

class { '::cinder::api':
  bind_host          => $bind_host,
  keystone_password  => hiera('CONFIG_CINDER_KS_PW'),
  keystone_tenant    => 'services',
  keystone_user      => 'cinder',
  auth_uri           => hiera('CONFIG_KEYSTONE_PUBLIC_URL'),
  identity_uri       => hiera('CONFIG_KEYSTONE_ADMIN_URL'),
}

class { '::cinder::scheduler': }

class { '::cinder::volume': }

class { '::cinder::client': }

# Cinder::Type requires keystone credentials
Cinder::Type {
  os_password    => hiera('CONFIG_CINDER_KS_PW'),
  os_tenant_name => 'services',
  os_username    => 'cinder',
  os_auth_url    => hiera('CONFIG_KEYSTONE_PUBLIC_URL'),
}

class { '::cinder::backends':
  enabled_backends => hiera_array('CONFIG_CINDER_BACKEND'),
}
