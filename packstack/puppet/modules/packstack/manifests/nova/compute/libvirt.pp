class packstack::nova::compute::libvirt ()
{
    # Ensure Firewall changes happen before libvirt service start
    # preventing a clash with rules being set by libvirt
    Firewall <| |> -> Class['::nova::compute::libvirt']

    $libvirt_vnc_bind_host = hiera('CONFIG_IP_VERSION') ? {
      'ipv6'  => '::0',
      default => '0.0.0.0',
      # TO-DO(mmagr): Add IPv6 support when hostnames are used
    }

    $libvirt_virt_type = hiera('CONFIG_NOVA_LIBVIRT_VIRT_TYPE')
    if $libvirt_virt_type == 'kvm' {
        # Workaround for bad /dev/kvm permissions
        # https://bugzilla.redhat.com/show_bug.cgi?id=950436
        file { '/dev/kvm':
          owner  => 'root',
          group  => 'kvm',
          mode   => '666',
        }

        # We have to fix the permissions after the installation has been done
        # and before the service is started.
        Package <| title == 'libvirt' |> ->
        File['/dev/kvm'] ->
        Service <| title == 'libvirt' |>
    }

    $migrate_transport = hiera('CONFIG_NOVA_COMPUTE_MIGRATE_PROTOCOL')
    if $migrate_transport == 'ssh' {
      $client_extraparams = {
        keyfile   => '/etc/nova/migration/identity',
      }
    } else {
      $client_extraparams = {}
    }

    class { '::nova::migration::libvirt':
      transport   => $migrate_transport,
      client_user => 'nova_migration',
      client_extraparams => $client_extraparams,
      require => Class['::nova::compute::libvirt']
    }

    class { '::nova::compute::libvirt':
      libvirt_virt_type        => $libvirt_virt_type,
      vncserver_listen         => $libvirt_vnc_bind_host,
      migration_support        => true,
    }

    # Remove libvirt's default network (usually virbr0) as it's unnecessary and
    # can be confusing
    exec {'virsh-net-destroy-default':
      onlyif  => '/usr/bin/virsh net-list | grep default',
      command => '/usr/bin/virsh net-destroy default',
      require => Service['libvirt'],
    }

    exec {'virsh-net-undefine-default':
      onlyif  => '/usr/bin/virsh net-list --inactive | grep default',
      command => '/usr/bin/virsh net-undefine default',
      require => Exec['virsh-net-destroy-default'],
    }

    $libvirt_debug = hiera('CONFIG_DEBUG_MODE')
    if $libvirt_debug {

      file_line { '/etc/libvirt/libvirt.conf log_filters':
        path   => '/etc/libvirt/libvirtd.conf',
        line   => 'log_filters = "1:libvirt 1:qemu 1:conf 1:security 3:event 3:json 3:file 1:util"',
        match  => 'log_filters =',
        notify => Service['libvirt'],
      }

      file_line { '/etc/libvirt/libvirt.conf log_outputs':
        path   => '/etc/libvirt/libvirtd.conf',
        line   => 'log_outputs = "1:file:/var/log/libvirt/libvirtd.log"',
        match  => 'log_outputs =',
        notify => Service['libvirt'],
      }

    }
}
