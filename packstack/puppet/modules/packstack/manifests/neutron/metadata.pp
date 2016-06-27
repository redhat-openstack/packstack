class packstack::neutron::metadata ()
{
    class { '::neutron::agents::metadata':
      shared_secret    => hiera('CONFIG_NEUTRON_METADATA_PW'),
      metadata_ip      => force_ip(hiera('CONFIG_KEYSTONE_HOST_URL')),
      debug            => hiera('CONFIG_DEBUG_MODE'),
      metadata_workers => hiera('CONFIG_SERVICE_WORKERS'),
    }
}
