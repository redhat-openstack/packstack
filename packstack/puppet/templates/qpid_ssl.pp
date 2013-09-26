# User and group for the nss database

group { 'qpidd':
    ensure => 'present',
}

user { 'qpidd':
    ensure     => 'present',
    managehome => true,
    home       => '/var/run/qpidd',
    require => Group['qpidd']
}

file { 'pid_dir':
    path => '/var/run/qpidd',
    ensure => directory,
    owner => 'qpidd',
    group => 'qpidd',
    require => User['qpidd'],
}

file_line { 'pid_dir_conf':
   path => $qpid::server::config_file,
   line => 'pid-dir=/var/run/qpidd',
   require => File['pid_dir'],
}

