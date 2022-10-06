class packstack::nova::neutron ()
{
    $nova_neutron_cfg_ctrl_host = lookup('CONFIG_KEYSTONE_HOST_URL')
    $neutron_auth_url = lookup('CONFIG_KEYSTONE_ADMIN_URL')

    class { 'nova::network::neutron':
      default_floating_pool => 'public',
      password              => lookup('CONFIG_NEUTRON_KS_PW'),
      auth_type             => 'v3password',
      project_name          => 'services',
      auth_url              => "${neutron_auth_url}/v3",
      region_name           => lookup('CONFIG_KEYSTONE_REGION'),
    }
}
