
$nova_neutron_cfg_ctrl_host = hiera('CONFIG_CONTROLLER_HOST')

class { 'nova::network::neutron':
  neutron_admin_password    => hiera('CONFIG_NEUTRON_KS_PW'),
  neutron_auth_strategy     => 'keystone',
  neutron_url               => "http://${nova_neutron_cfg_ctrl_host}:9696",
  neutron_admin_tenant_name => 'services',
  neutron_admin_auth_url    => "http://${nova_neutron_cfg_ctrl_host}:35357/v2.0",
  neutron_region_name       => hiera('CONFIG_KEYSTONE_REGION'),
}

class { 'nova::compute::neutron':
  libvirt_vif_driver => hiera('CONFIG_NOVA_LIBVIRT_VIF_DRIVER'),
}
