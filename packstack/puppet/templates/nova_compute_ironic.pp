$ironic_config_controller_host = hiera('CONFIG_CONTROLLER_HOST')

class {'nova::compute::ironic':
  admin_user        => 'ironic',
  admin_passwd      => hiera('CONFIG_IRONIC_KS_PW'),
  admin_url         => "http://${ironic_config_controller_host}:35357/v2.0",
  admin_tenant_name => 'services',
  api_endpoint      => "http://${ironic_config_controller_host}:6385/v1",
}
