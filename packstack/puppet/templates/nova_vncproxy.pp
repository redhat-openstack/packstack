if hiera('CONFIG_HORIZON_SSL') == 'y' {
  nova_config {
    'DEFAULT/ssl_only': value => true;
    'DEFAULT/cert':     value => hiera('CONFIG_VNC_SSL_CERT');
    'DEFAULT/key':      value => hiera('CONFIG_VNC_SSL_KEY');
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

