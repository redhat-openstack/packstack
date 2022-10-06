class packstack::nova::compute::ironic ()
{
  $ironic_config_controller_host = lookup('CONFIG_KEYSTONE_HOST_URL')
  $ironic_config_keystone_admin = lookup('CONFIG_KEYSTONE_ADMIN_URL')

  class { 'nova::ironic::common':
      username     => 'ironic',
      password     => lookup('CONFIG_IRONIC_KS_PW'),
      auth_url     => $ironic_config_keystone_admin,
      project_name => 'services',
      api_endpoint => "http://${ironic_config_controller_host}:6385/v1",
  }

   include nova::compute::ironic
}
