
class {"qpid::server":
    auth => "no"
}

firewall { '001 qpid incomming':
    proto    => 'tcp',
    dport    => ['5672'],
    action   => 'accept',
}

