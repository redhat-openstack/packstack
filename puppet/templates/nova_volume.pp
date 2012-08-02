
class {"nova::volume":
    enabled => true,
}
    
class {"nova::volume::iscsi":}

firewall { '001 volume incomming':
    proto    => 'tcp',
    dport    => ['3260'],
    action   => 'accept',
}
