
class {"qpid::server":
    config_file => $::operatingsystem? {
        'Fedora' => '/etc/qpid/qpidd.conf',
        default  => '/etc/qpidd.conf',
        },
    auth => "no",
    clustered => false,
}

firewall { '001 qpid incoming':
    proto    => 'tcp',
    dport    => ['5672'],
    action   => 'accept',
}
