class packstack::nova::compute ()
{
    $my_ip = choose_my_ip(lookup('HOST_LIST'))
    $my_ip_without_dot = regsubst($my_ip, '\.', '_', 'G')
    $qemu_rule_name = "FIREWALL_NOVA_QEMU_MIG_RULES_${my_ip_without_dot}"
    create_resources(packstack::firewall, lookup($qemu_rule_name, undef, undef, {}))
    create_resources(packstack::firewall, lookup('FIREWALL_NOVA_COMPUTE_RULES', undef, undef, {}))

    ensure_packages(['/usr/bin/cinder'], {'ensure' => 'present'})
    Package['/usr/bin/cinder'] -> Class['nova']

    # Install the private key to be used for live migration.  This needs to be
    # configured into libvirt/live_migration_uri in nova.conf.
    $migrate_transport = lookup('CONFIG_NOVA_COMPUTE_MIGRATE_PROTOCOL')
    if $migrate_transport == 'ssh' {
      ensure_packages(['openstack-nova-migration'], {'ensure' => 'present'})

      file { '/etc/nova/migration/identity':
        content => lookup('NOVA_MIGRATION_KEY_SECRET'),
        mode    => '0600',
        owner   => nova,
        group   => nova,
        require => Package['openstack-nova-migration'],
      }

      $key_type = lookup('NOVA_MIGRATION_KEY_TYPE')
      $key_content = lookup('NOVA_MIGRATION_KEY_PUBLIC')

      file { '/etc/nova/migration/authorized_keys':
        content => "${key_type} ${key_content}",
        mode    => '0640',
        owner   => root,
        group   => nova_migration,
        require => Package['openstack-nova-migration'],
      }

      augeas{'Match block for user nova_migration':
        context => '/files/etc/ssh/sshd_config',
        changes => [
          'set Match[User nova_migration]/Condition/User nova_migration',
          'set Match[Condition/User = "nova_migration"]/Settings/AllowTcpForwarding no',
          'set Match[Condition/User = "nova_migration"]/Settings/AuthorizedKeysFile /etc/nova/migration/authorized_keys',
          'set Match[Condition/User = "nova_migration"]/Settings/ForceCommand /bin/nova-migration-wrapper',
          'set Match[Condition/User = "nova_migration"]/Settings/PasswordAuthentication no',
          'set Match[Condition/User = "nova_migration"]/Settings/X11Forwarding no',
        ],
        onlyif  => 'match Match[Condition/User = "nova_migration"] size == 0',
        notify  => Service['sshd']
      }

      service {'sshd':
        ensure  => running,
      }
    }

    if ($facts['networking']['fqdn'] == '' or $facts['networking']['fqdn'] =~ /localhost/) {
      # For cases where FQDNs have not been correctly set
      $vncproxy_server = choose_my_ip(lookup('HOST_LIST'))
    } else {
      $vncproxy_server = $facts['networking']['fqdn']
    }

    if lookup('CONFIG_CEILOMETER_INSTALL') == 'y' {
      $instance_usage_audit = true
      $instance_usage_audit_period = 'hour'
    } else {
      $instance_usage_audit = false
      $instance_usage_audit_period = 'month'
    }

    class { 'nova::compute::pci':
      passthrough => lookup('CONFIG_NOVA_PCI_PASSTHROUGH_WHITELIST')
    }

    class { 'nova::compute':
      enabled                       => true,
      vncproxy_host                 => lookup('CONFIG_KEYSTONE_HOST_URL'),
      vncproxy_protocol             => lookup('CONFIG_VNCPROXY_PROTOCOL'),
      vncserver_proxyclient_address => $vncproxy_server,
      instance_usage_audit          => $instance_usage_audit,
      instance_usage_audit_period   => $instance_usage_audit_period,
      force_config_drive            => false,
      mkisofs_cmd                   => 'mkisofs',
    }

    class { 'nova::placement':
      auth_url    => lookup('CONFIG_KEYSTONE_PUBLIC_URL'),
      password    => lookup('CONFIG_NOVA_KS_PW'),
      region_name => lookup('CONFIG_KEYSTONE_REGION'),
    }

    # Tune the host with a virtual hosts profile
    ensure_packages(['tuned'], {'ensure' => 'present'})

    service { 'tuned':
      ensure  => running,
      require => Package['tuned'],
    }

    # tries/try_sleep to try and circumvent rhbz1320744
    exec { 'tuned-virtual-host':
      unless    => '/usr/sbin/tuned-adm active | /bin/grep virtual-host',
      command   => '/usr/sbin/tuned-adm profile virtual-host',
      require   => Service['tuned'],
      tries     => 3,
      try_sleep => 5
    }
}
