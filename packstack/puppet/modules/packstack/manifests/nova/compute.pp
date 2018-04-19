class packstack::nova::compute ()
{
    $my_ip = choose_my_ip(hiera('HOST_LIST'))
    $qemu_rule_name = "FIREWALL_NOVA_QEMU_MIG_RULES_${my_ip}"
    create_resources(packstack::firewall, hiera($qemu_rule_name, {}))
    create_resources(packstack::firewall, hiera('FIREWALL_NOVA_COMPUTE_RULES', {}))

    ensure_packages(['python-cinderclient'], {'ensure' => 'present'})
    Package['python-cinderclient'] -> Class['nova']

    # Install the private key to be used for live migration.  This needs to be
    # configured into libvirt/live_migration_uri in nova.conf.
    $migrate_transport = hiera('CONFIG_NOVA_COMPUTE_MIGRATE_PROTOCOL')
    if $migrate_transport == 'ssh' {
      ensure_packages(['openstack-nova-migration'], {'ensure' => 'present'})

      file { '/etc/nova/migration/identity':
        content => hiera('NOVA_MIGRATION_KEY_SECRET'),
        mode    => '0600',
        owner   => root,
        group   => root,
        require => Package['openstack-nova-migration'],
      }

      $key_type = hiera('NOVA_MIGRATION_KEY_TYPE')
      $key_content = hiera('NOVA_MIGRATION_KEY_PUBLIC')

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
        onlyif => 'match Match[Condition/User = "nova_migration"] size == 0',
        notify => Service['sshd']
      }

      service {'sshd':
        ensure  => running,
      }
    }

    nova_config{
      'DEFAULT/volume_api_class':
        value => 'nova.volume.cinder.API';
    }

    if ($::fqdn == '' or $::fqdn =~ /localhost/) {
      # For cases where FQDNs have not been correctly set
      $vncproxy_server = choose_my_ip(hiera('HOST_LIST'))
    } else {
      $vncproxy_server = $::fqdn
    }

    if hiera('CONFIG_CEILOMETER_INSTALL') == 'y' {
      $instance_usage_audit = true
      $instance_usage_audit_period = 'hour'
    } else {
      $instance_usage_audit = false
      $instance_usage_audit_period = 'month'
    }

    class { '::nova::compute':
      enabled                       => true,
      vncproxy_host                 => hiera('CONFIG_KEYSTONE_HOST_URL'),
      vncproxy_protocol             => hiera('CONFIG_VNCPROXY_PROTOCOL'),
      vncserver_proxyclient_address => $vncproxy_server,
      instance_usage_audit          => $instance_usage_audit,
      instance_usage_audit_period   => $instance_usage_audit_period,
      allow_resize_to_same_host     => hiera('CONFIG_NOVA_ALLOW_RESIZE_TO_SAME'),
      force_config_drive            => false,
    }

    class { '::nova::placement':
      auth_url       => hiera('CONFIG_KEYSTONE_PUBLIC_URL'),
      password       => hiera('CONFIG_NOVA_KS_PW'),
      os_region_name => hiera('CONFIG_KEYSTONE_REGION'),
    }

    class { '::nova::compute::pci':
      passthrough => hiera('CONFIG_NOVA_PCI_PASSTHROUGH_WHITELIST')
    }

    include ::nova::cell_v2::discover_hosts

    Class['nova::compute'] ~> Class['nova::cell_v2::discover_hosts']

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
