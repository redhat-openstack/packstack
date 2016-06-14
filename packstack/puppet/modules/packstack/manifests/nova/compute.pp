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
    file { '/etc/nova/ssh':
      ensure  => directory,
      owner   => root,
      group   => root,
      mode    => '0700',
      require => Package['nova-common'],
    }

    file { '/etc/nova/ssh/nova_migration_key':
      content => hiera('NOVA_MIGRATION_KEY_SECRET'),
      mode    => '0600',
      owner   => root,
      group   => root,
      require => File['/etc/nova/ssh'],
    }

    nova_config{
      'DEFAULT/volume_api_class':
        value => 'nova.volume.cinder.API';
      'libvirt/live_migration_uri':
        value => hiera('CONFIG_NOVA_COMPUTE_MIGRATE_URL');
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
      compute_manager               => hiera('CONFIG_NOVA_COMPUTE_MANAGER'),
      pci_passthrough               => hiera('CONFIG_NOVA_PCI_PASSTHROUGH_WHITELIST'),
      instance_usage_audit          => $instance_usage_audit,
      instance_usage_audit_period   => $instance_usage_audit_period,
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
