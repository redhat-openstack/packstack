$neutron_notif_cfg_ctrl_host = hiera('CONFIG_CONTROLLER_HOST')

# Configure nova notifications system
class { 'neutron::server::notifications':
  nova_admin_username    => 'nova',
  nova_admin_password    => hiera('CONFIG_NOVA_KS_PW'),
  nova_admin_tenant_name => 'services',
  nova_url               => "http://${neutron_notif_cfg_ctrl_host}:8774/v2",
  nova_admin_auth_url    => "http://${neutron_notif_cfg_ctrl_host}:35357/v2.0",
  nova_region_name       => hiera('CONFIG_KEYSTONE_REGION'),
}
