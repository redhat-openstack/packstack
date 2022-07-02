class packstack::neutron::metadata ()
{
    class { 'neutron::agents::metadata':
      shared_secret    => lookup('CONFIG_NEUTRON_METADATA_PW'),
      metadata_host    => force_ip(lookup('CONFIG_KEYSTONE_HOST_URL')),
      debug            => lookup('CONFIG_DEBUG_MODE'),
      metadata_workers => lookup('CONFIG_SERVICE_WORKERS'),
    }
}
