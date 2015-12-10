$neutron_notif_cfg_ctrl_host = hiera('CONFIG_KEYSTONE_HOST_URL')

# Configure nova notifications system
class { '::neutron::server::notifications':
  username    => 'nova',
  password    => hiera('CONFIG_NOVA_KS_PW'),
  tenant_name => 'services',
  nova_url    => "http://${neutron_notif_cfg_ctrl_host}:8774/v2",
  auth_url    => hiera('CONFIG_KEYSTONE_ADMIN_URL'),
  region_name => hiera('CONFIG_KEYSTONE_REGION'),
}
