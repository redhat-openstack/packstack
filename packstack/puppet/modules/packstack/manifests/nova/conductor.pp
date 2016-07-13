class packstack::nova::conductor ()
{
    class { '::nova::conductor':
      enabled => true,
      workers => hiera('CONFIG_SERVICE_WORKERS'),
    }
}
