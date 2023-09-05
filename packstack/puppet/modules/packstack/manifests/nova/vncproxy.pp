class packstack::nova::vncproxy ()
{
    $vnc_bind_host = lookup('CONFIG_IP_VERSION') ? {
      'ipv6'  => '::0',
      default => '0.0.0.0',
      # TO-DO(mmagr): Add IPv6 support when hostnames are used
    }

    class { 'nova::vncproxy':
      enabled => true,
      host    => $vnc_bind_host,
    }

    firewall { '001 novncproxy incoming':
      proto  => 'tcp',
      dport  => ['6080'],
      jump   => 'accept',
    }
}
