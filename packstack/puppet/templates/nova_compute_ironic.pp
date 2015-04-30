$ironic_config_controller_host = hiera('CONFIG_KEYSTONE_HOST_URL')

class { '::nova::compute::ironic':
  admin_user        => 'ironic',
  admin_passwd      => hiera('CONFIG_IRONIC_KS_PW'),
  admin_url         => hiera('CONFIG_KEYSTONE_ADMIN_URL'),
  admin_tenant_name => 'services',
  api_endpoint      => "http://${ironic_config_controller_host}:6385/v1",
}
