# User and group for the nss database

group { 'qpidd':
    ensure => 'present',
}

exec { 'stop_qpid' :
        command => '/sbin/service qpidd stop',
        onlyif  => '/sbin/service qpidd status',
}

user { 'qpidd':
    ensure     => 'present',
    managehome => true,
    home       => '/var/run/qpidd',
    gid        => 'qpidd',
    before     => Class['qpid::server']
}

Exec['stop_qpid']->User['qpidd']

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

