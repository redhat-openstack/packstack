class packstack::nova::vncproxy ()
{
    if hiera('CONFIG_HORIZON_SSL') == 'y' {
      nova_config {
        'DEFAULT/ssl_only': value => true;
        'DEFAULT/cert':     value => hiera('CONFIG_VNC_SSL_CERT');
        'DEFAULT/key':      value => hiera('CONFIG_VNC_SSL_KEY');
      }
    }

    $vnc_bind_host = hiera('CONFIG_IP_VERSION') ? {
      'ipv6'  => '::0',
      default => '0.0.0.0',
      # TO-DO(mmagr): Add IPv6 support when hostnames are used
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
}
