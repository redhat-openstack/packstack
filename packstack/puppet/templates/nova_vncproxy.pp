class {"nova::vncproxy":
    enabled => true,
}

class {"nova::consoleauth":
    enabled => true,
}

firewall { '001 novncproxy incomming':
    proto    => 'tcp',
    dport    => ['6080'],
    action   => 'accept',
}

