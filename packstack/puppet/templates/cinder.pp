cinder_config {
  'DEFAULT/glance_host': value => hiera('CONFIG_STORAGE_HOST_URL');
}

$bind_host = hiera('CONFIG_IP_VERSION') ? {
  'ipv6'  => '::0',
  default => '0.0.0.0',
  # TO-DO(mmagr): Add IPv6 support when hostnames are used
}

$cinder_keystone_url = regsubst(regsubst(hiera('CONFIG_KEYSTONE_PUBLIC_URL'),'/v2.0',''),'/v3','')

class { '::cinder::api':
  bind_host               => $bind_host,
  keystone_password       => hiera('CONFIG_CINDER_KS_PW'),
  keystone_tenant         => 'services',
  keystone_user           => 'cinder',
  auth_uri                => $cinder_keystone_url,
  identity_uri            => hiera('CONFIG_KEYSTONE_ADMIN_URL'),
  nova_catalog_info       => 'compute:nova:publicURL',
  nova_catalog_admin_info => 'compute:nova:adminURL',
  service_workers         => $service_workers
}

class { '::cinder::scheduler': }

class { '::cinder::volume': }

class { '::cinder::client': }

class { '::cinder::backends':
  enabled_backends => hiera_array('CONFIG_CINDER_BACKEND'),
}

$db_purge = hiera('CONFIG_CINDER_DB_PURGE_ENABLE')
if $db_purge {
  class { '::cinder::cron::db_purge':
    hour        => '*/24',
    destination => '/dev/null',
    age         => 1
  }
}
