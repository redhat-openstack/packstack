$bind_host = hiera('CONFIG_IP_VERSION') ? {
  'ipv6' => '::0',
  'ipv4' => '0.0.0.0',
}

class { '::trove::api':
  bind_host         => $bind_host,
  enabled           => true,
  keystone_password => hiera('CONFIG_TROVE_KS_PW'),
  auth_host         => hiera('CONFIG_KEYSTONE_HOST_URL'),
  auth_port         => 35357,
  cert_file         => false,
  key_file          => false,
  ca_file           => false,
  verbose           => true,
  debug             => hiera('CONFIG_DEBUG_MODE'),
}

$trove_cfg_ctrl_host = hiera('CONFIG_KEYSTONE_HOST_URL')

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
