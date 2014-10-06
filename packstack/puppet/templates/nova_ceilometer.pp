$nova_ceil_cfg_ctrl_host = hiera('CONFIG_CONTROLLER_HOST')

class { 'ceilometer::agent::auth':
  auth_url      => "http://${nova_ceil_cfg_ctrl_host}:35357/v2.0",
  auth_password => hiera('CONFIG_CEILOMETER_KS_PW'),
}

class { 'ceilometer::agent::compute': }

