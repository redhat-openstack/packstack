$bind_host = hiera('CONFIG_IP_VERSION') ? {
  'ipv6'  => '::0',
  default => '0.0.0.0',
  # TO-DO(mmagr): Add IPv6 support when hostnames are used
}

class { '::trove::api':
  bind_host         => $bind_host,
  enabled           => true,
  keystone_password => hiera('CONFIG_TROVE_KS_PW'),
  auth_url          => hiera('CONFIG_KEYSTONE_PUBLIC_URL'),
  cert_file         => false,
  key_file          => false,
  ca_file           => false,
  verbose           => true,
  debug             => hiera('CONFIG_DEBUG_MODE'),
  workers           => $service_workers
}

class { '::trove::conductor':
  auth_url => hiera('CONFIG_KEYSTONE_PUBLIC_URL'),
  verbose  => true,
  debug    => hiera('CONFIG_DEBUG_MODE'),
}

class { '::trove::taskmanager':
  auth_url => hiera('CONFIG_KEYSTONE_PUBLIC_URL'),
  verbose  => true,
  debug    => hiera('CONFIG_DEBUG_MODE'),
}
