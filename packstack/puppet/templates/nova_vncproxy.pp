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

$vnc_bind_host = hiera('CONFIG_IP_VERSION') ? {
  'ipv6' => '::0',
  'ipv4' => '0.0.0.0',
}

class { '::nova::vncproxy':
  enabled => true,
  host    => $vnc_bind_host,
}

class { '::nova::consoleauth':
  enabled => true,
}

firewall { '001 novncproxy incoming':
  proto  => 'tcp',
  dport  => ['6080'],
  action => 'accept',
}

