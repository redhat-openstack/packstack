# Create firewall rules to allow only the FIREWALL_ALLOWED
# hosts that need to connect via FIREWALL_PORTS
# using FIREWALL_CHAIN

define packstack::firewall($host, $service_name, $chain = "INPUT", $ports = undef, $proto = 'tcp') {
  $source = $host ? {
    'ALL' => '0.0.0.0/0',
    default => $host,
  }
  $heading = $chain ? {
    'OUTPUT' => 'outgoing',
    default => 'incoming',
  }

  if $ports == undef {
    firewall { "001 ${service_name} ${heading} ${title}":
      chain => $chain,
      proto  => $proto,
      action => 'accept',
      source => $source,
    }
  }
  else {
    firewall { "001 ${service_name} ${heading} ${title}":
      chain => $chain,
      proto  => $proto,
      dport  => $ports,
      action => 'accept',
      source => $source,
    }
  }
}
