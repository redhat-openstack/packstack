class packstack::nova::neutron ()
{
    $nova_neutron_cfg_ctrl_host = hiera('CONFIG_KEYSTONE_HOST_URL')
    $neutron_auth_url = hiera('CONFIG_KEYSTONE_ADMIN_URL')

    class { '::nova::network::neutron':
      default_floating_pool => 'public',
      neutron_password      => hiera('CONFIG_NEUTRON_KS_PW'),
      neutron_auth_type     => 'v3password',
      neutron_url           => "http://${nova_neutron_cfg_ctrl_host}:9696",
      neutron_project_name  => 'services',
      neutron_auth_url      => "${neutron_auth_url}/v3",
      neutron_region_name   => hiera('CONFIG_KEYSTONE_REGION'),
      neutron_url_timeout   => '60',
    }

    class { '::nova::compute::neutron':
      libvirt_vif_driver => hiera('CONFIG_NOVA_LIBVIRT_VIF_DRIVER'),
    }
}
