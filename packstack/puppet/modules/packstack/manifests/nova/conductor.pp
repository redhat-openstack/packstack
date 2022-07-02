class packstack::nova::conductor ()
{
    class { 'nova::conductor':
      enabled => true,
      workers => lookup('CONFIG_SERVICE_WORKERS'),
    }

    Keystone_endpoint <||> -> Service['nova-conductor']
    Keystone_service <||> -> Service['nova-conductor']
}
