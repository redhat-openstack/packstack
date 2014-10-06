$neutron_metadata_cfg_ctrl_host = hiera('CONFIG_CONTROLLER_HOST')

class { 'neutron::agents::metadata':
  auth_password => hiera('CONFIG_NEUTRON_KS_PW'),
  auth_url      => "http://${neutron_metadata_cfg_ctrl_host}:35357/v2.0",
  auth_region   => hiera('CONFIG_KEYSTONE_REGION'),
  shared_secret => hiera('CONFIG_NEUTRON_METADATA_PW'),
  metadata_ip   => hiera('CONFIG_CONTROLLER_HOST'),
  debug         => hiera('CONFIG_DEBUG_MODE'),
}
