cinder_config {
  'DEFAULT/glance_host': value => hiera('CONFIG_STORAGE_HOST');
}

package { 'python-keystone':
  notify => Class['cinder::api'],
}

class { 'cinder::api':
  keystone_password  => hiera('CONFIG_CINDER_KS_PW'),
  keystone_tenant    => 'services',
  keystone_user      => 'cinder',
  keystone_auth_host => hiera('CONFIG_CONTROLLER_HOST'),
}

class { 'cinder::scheduler': }

class { 'cinder::volume': }

class { 'cinder::client': }

$cinder_config_controller_host = hiera('CONFIG_CONTROLLER_HOST')

# Cinder::Type requires keystone credentials
Cinder::Type {
  os_password    => hiera('CONFIG_CINDER_KS_PW'),
  os_tenant_name => 'services',
  os_username    => 'cinder',
  os_auth_url    => "http://${cinder_config_controller_host}:5000/v2.0/",
}

class { 'cinder::backends':
  enabled_backends => hiera_array('CONFIG_CINDER_BACKEND'),
}
