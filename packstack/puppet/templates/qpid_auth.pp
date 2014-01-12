qpid_user { '%(CONFIG_QPID_AUTH_USER)s':
    password  => '%(CONFIG_QPID_AUTH_PASSWORD)s',
    file  => '/var/lib/qpidd/qpidd.sasldb',
    realm  => 'QPID',
    provider => 'saslpasswd2',
    require   => Class['qpid::server'],
}

file { 'sasldb_file':
    path => '/var/lib/qpidd/qpidd.sasldb',
    ensure => file,
    owner => 'qpidd',
    group => 'qpidd',
}

