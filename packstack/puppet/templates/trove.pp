$bind_host = hiera('CONFIG_IP_VERSION') ? {
  'ipv6'  => '::0',
  default => '0.0.0.0',
  # TO-DO(mmagr): Add IPv6 support when hostnames are used
}

class { '::trove::api':
  bind_host         => $bind_host,
  enabled           => true,
  keystone_password => hiera('CONFIG_TROVE_KS_PW'),
  auth_uri          => hiera('CONFIG_KEYSTONE_PUBLIC_URL'),
  identity_uri      => hiera('CONFIG_KEYSTONE_ADMIN_URL'),
  cert_file         => false,
  key_file          => false,
  ca_file           => false,
  verbose           => true,
  debug             => hiera('CONFIG_DEBUG_MODE'),
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

trove_config {
  # TO-DO: Remove this as soon as bz#1298245 is resolved.
  'DEFAULT/api_paste_config':  value => '/usr/share/trove/trove-dist-paste.ini';
  # TO-DO: Remove this workaround as soon as module support is implemented (see rhbz#1300662)
  'keystone_authtoken/auth_version' : value => hiera('CONFIG_KEYSTONE_API_VERSION');
}
