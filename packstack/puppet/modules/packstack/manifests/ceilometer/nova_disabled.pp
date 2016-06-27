class packstack::ceilometer::nova_disabled ()
{
    group { 'nova':
      ensure => present,
    }

    Group['nova'] -> Class['ceilometer']
}
