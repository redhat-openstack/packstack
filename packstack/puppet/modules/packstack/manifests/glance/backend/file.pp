class packstack::glance::backend::file ()
{
    # TO-DO: Make this configurable
    class { '::glance::backend::file':
      filesystem_store_datadir => '/var/lib/glance/images/',
    }
}
