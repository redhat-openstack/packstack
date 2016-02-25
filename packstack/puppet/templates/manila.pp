manila_config {
  'DEFAULT/glance_host': value => hiera('CONFIG_STORAGE_HOST_URL');
}

$bind_host = hiera('CONFIG_IP_VERSION') ? {
  'ipv6'  => '::0',
  default => '0.0.0.0',
  # TO-DO(mmagr): Add IPv6 support when hostnames are used
}

class { '::manila::api':
  bind_host          => $bind_host,
  keystone_password  => hiera('CONFIG_MANILA_KS_PW'),
  keystone_tenant    => 'services',
  keystone_user      => 'manila',
  keystone_auth_uri  => hiera('CONFIG_KEYSTONE_PUBLIC_URL'),
}

class { '::manila::scheduler':
}

class { '::manila::share':
}

class { '::manila::backends':
  enabled_share_backends => hiera('CONFIG_MANILA_BACKEND'),
}
