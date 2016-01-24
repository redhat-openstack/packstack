$ironic_config_controller_host = hiera('CONFIG_KEYSTONE_HOST_URL')
$ironic_config_keystone_admin = hiera('CONFIG_KEYSTONE_ADMIN_URL')
$ironic_config_keystone_version = hiera('CONFIG_KEYSTONE_API_VERSION')

class { '::nova::compute::ironic':
  admin_user        => 'ironic',
  admin_passwd      => hiera('CONFIG_IRONIC_KS_PW'),
  admin_url         => "${ironic_config_keystone_admin}/${ironic_config_keystone_version}",
  admin_tenant_name => 'services',
  api_endpoint      => "http://${ironic_config_controller_host}:6385/v1",
}
