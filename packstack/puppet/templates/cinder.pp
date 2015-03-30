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
  keystone_auth_host => hiera('CONFIG_KEYSTONE_HOST_URL'),
}

class { '::cinder::scheduler': }

class { '::cinder::volume': }

class { '::cinder::client': }

$cinder_config_controller_host = hiera('CONFIG_KEYSTONE_HOST_URL')

# Cinder::Type requires keystone credentials
Cinder::Type {
  os_password    => hiera('CONFIG_CINDER_KS_PW'),
  os_tenant_name => 'services',
  os_username    => 'cinder',
  os_auth_url    => "http://${cinder_config_controller_host}:5000/v2.0/",
}

class { '::cinder::backends':
  enabled_backends => hiera_array('CONFIG_CINDER_BACKEND'),
}
