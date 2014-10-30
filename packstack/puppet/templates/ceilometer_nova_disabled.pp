group { 'nova':
  ensure => present,
}

Group['nova'] -> Class['ceilometer']

