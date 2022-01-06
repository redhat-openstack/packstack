class packstack::glance::backend::file ()
{
    glance::backend::multistore::file { 'file':
      filesystem_store_datadir => '/var/lib/glance/images/',
    }
}
