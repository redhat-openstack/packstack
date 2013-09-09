
class {"qpid::server":
    auth => "no",
    clustered => false,
}

firewall { '001 qpid incoming':
    proto    => 'tcp',
    dport    => ['5672'],
    action   => 'accept',
}
