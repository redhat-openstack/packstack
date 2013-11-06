# Create firewall rules to allow only the hosts that need to connect
# to %(FIREWALL_SERVICE_NAME)s

$hosts = [ %(FIREWALL_ALLOWED)s ]

define add_allow_host {
    $source = $title ? {
        'ALL' => '0.0.0.0/0',
        default => $title,
    }
    firewall { "001 %(FIREWALL_SERVICE_NAME)s incoming ${title}":
        proto  => 'tcp',
        dport  => [%(FIREWALL_PORTS)s],
        action => 'accept',
        source => $source,
    }
}

add_allow_host {$hosts:}
