$nova_neutron_cfg_ctrl_host = hiera('CONFIG_KEYSTONE_HOST_URL')

class { '::nova::network::neutron':
  neutron_password    => hiera('CONFIG_NEUTRON_KS_PW'),
  neutron_auth_plugin => 'password',
  neutron_url         => "http://${nova_neutron_cfg_ctrl_host}:9696",
  neutron_tenant_name => 'services',
  neutron_auth_url    => hiera('CONFIG_KEYSTONE_ADMIN_URL'),
  neutron_region_name => hiera('CONFIG_KEYSTONE_REGION'),
}

class { '::nova::compute::neutron':
  libvirt_vif_driver => hiera('CONFIG_NOVA_LIBVIRT_VIF_DRIVER'),
}
