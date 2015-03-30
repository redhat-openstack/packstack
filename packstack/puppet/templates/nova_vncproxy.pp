if $is_horizon_ssl == undef {
  $is_horizon_ssl = hiera('CONFIG_HORIZON_SSL')
}

if $is_horizon_ssl == true {
  nova_config {
    'DEFAULT/ssl_only': value => true;
    'DEFAULT/cert':     value => '/etc/nova/nova.crt';
    'DEFAULT/key':      value => '/etc/nova/nova.key';
  }
}

if $vncproxy_protocol == undef {
  $vncproxy_protocol = $is_horizon_ssl ? {
    true    => 'https',
    false   => 'http',
    default => 'http',
  }
}

class { 'nova::vncproxy':
  enabled           => true,
  host              => hiera('CONFIG_CONTROLLER_HOST'),
  vncproxy_protocol => $vncproxy_protocol,
}

class { 'nova::consoleauth':
  enabled => true,
}

firewall { '001 novncproxy incoming':
  proto  => 'tcp',
  dport  => ['6080'],
  action => 'accept',
}

