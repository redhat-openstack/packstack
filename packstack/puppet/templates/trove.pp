class { '::trove::api':
  enabled           => true,
  keystone_password => hiera('CONFIG_TROVE_KS_PW'),
  auth_host         => hiera('CONFIG_CONTROLLER_HOST'),
  auth_port         => 35357,
  cert_file         => false,
  key_file          => false,
  ca_file           => false,
  verbose           => true,
  debug             => hiera('CONFIG_DEBUG_MODE'),
}

$trove_cfg_ctrl_host = hiera('CONFIG_CONTROLLER_HOST')

class { '::trove::conductor':
  auth_url => "http://${trove_cfg_ctrl_host}:5000/v2.0",
  verbose  => true,
  debug    => hiera('CONFIG_DEBUG_MODE'),
}

class { '::trove::taskmanager':
  auth_url => "http://${trove_cfg_ctrl_host}:5000/v2.0",
  verbose  => true,
  debug    => hiera('CONFIG_DEBUG_MODE'),
}
