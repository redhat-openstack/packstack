class {"nova::vncproxy":
    enabled => true,
}

class {"nova::consoleauth":
    enabled => true,
}

firewall { '001 novncproxy incoming':
    proto    => 'tcp',
    dport    => ['6080'],
    action   => 'accept',
}

