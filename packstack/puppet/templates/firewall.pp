# Create firewall rules to allow only the hosts that need to connect
# to %(FIREWALL_SERVICE_NAME)s

$hosts = [ %(FIREWALL_ALLOWED)s ]

define add_allow_host {
    firewall { "001 %(FIREWALL_SERVICE_NAME)s incoming ${title}":
        proto  => 'tcp',
        dport  => [%(FIREWALL_PORTS)s],
        action => 'accept',
        source => $title,
    }
}

add_allow_host { $hosts:}
