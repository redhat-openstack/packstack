class { '::neutron::agents::metadata':
  auth_password    => hiera('CONFIG_NEUTRON_KS_PW'),
  auth_url         => hiera('CONFIG_KEYSTONE_PUBLIC_URL'),
  auth_region      => hiera('CONFIG_KEYSTONE_REGION'),
  shared_secret    => hiera('CONFIG_NEUTRON_METADATA_PW'),
  metadata_ip      => force_ip(hiera('CONFIG_KEYSTONE_HOST_URL')),
  debug            => hiera('CONFIG_DEBUG_MODE'),
  metadata_workers => $service_workers
}
