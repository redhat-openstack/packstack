# Create firewall rules to allow only the FIREWALL_ALLOWED
# hosts that need to connect via FIREWALL_PORTS
# using FIREWALL_CHAIN

define packstack::firewall (
  $host,
  $service_name,
  $chain = 'INPUT',
  $ports = undef,
  $proto = 'tcp'
) {
  $ip_version = lookup('CONFIG_IP_VERSION')

  $protocol = $ip_version ? {
    'ipv6'  => 'ip6tables',
    default => 'iptables',
    # TO-DO(mmagr): Add IPv6 support when hostnames are used
  }

  $source = $host ? {
    'ALL' => $ip_version ? {
      'ipv6'  => '::/0',
      default => '0.0.0.0/0'
    },
    default => $host,
  }

  $heading = $chain ? {
    'OUTPUT' => 'outgoing',
    default => 'incoming',
  }

  if $ports == undef {
    firewall { "001 ${service_name} ${heading} ${title}":
      chain    => $chain,
      proto    => $proto,
      jump     => 'accept',
      source   => $source,
      protocol => $protocol,
    }
  }
  else {
    firewall { "001 ${service_name} ${heading} ${title}":
      chain    => $chain,
      proto    => $proto,
      dport    => $ports,
      jump     => 'accept',
      source   => $source,
      protocol => $protocol,
    }
  }
}
