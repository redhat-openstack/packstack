package{'python-cinderclient':
    before => Class["nova"]
}

# Install the private key to be used for live migration.  This needs to be configured
# into libvirt/live_migration_uri in nova.conf.
file { '/etc/nova/ssh':
  ensure => directory,
  owner  => root,
  group  => root,
  mode   => 0700,
}

file { '/etc/nova/ssh/nova_migration_key':
  content => '%(NOVA_MIGRATION_KEY_SECRET)s',
  mode    => 0600,
  owner   => root,
  group   => root,
  require => File['/etc/nova/ssh'],
}

nova_config{
    "DEFAULT/volume_api_class": value   => "nova.volume.cinder.API";
    "libvirt/live_migration_uri": value => "qemu+ssh://nova@%%s/system?keyfile=/etc/nova/ssh/nova_migration_key";
}

class {"nova::compute":
    enabled => true,
    vncproxy_host => "%(CONFIG_NOVA_VNCPROXY_HOST)s",
    vncserver_proxyclient_address => "%(CONFIG_NOVA_COMPUTE_HOST)s",
}


# Note : remove this once we're installing a version of openstack that isn't
#        supported on RHEL 6.3
if $::is_virtual_packstack == "true" and $::osfamily == "RedHat" and
    $::operatingsystemrelease == "6.3"{
    file { "/usr/bin/qemu-system-x86_64":
        ensure => link,
        target => "/usr/libexec/qemu-kvm",
        notify => Service["nova-compute"],
    }
}

# Tune the host with a virtual hosts profile
package {'tuned':
    ensure => present,
}

service {'tuned':
    ensure => running,
    require => Package['tuned'],
}

if $::operatingsystem == 'Fedora' and $::operatingsystemrelease == 19 {
    # older tuned service is sometimes stucked on Fedora 19
    exec {'tuned-update':
       path => ['/sbin', '/usr/sbin', '/bin', '/usr/bin'],
       command => 'yum update -y tuned',
       logoutput => 'on_failure',
    }

    exec {'tuned-restart':
       path => ['/sbin', '/usr/sbin', '/bin', '/usr/bin'],
       command => 'systemctl restart tuned.service',
       logoutput => 'on_failure',
    }

    Service['tuned'] -> Exec['tuned-update'] -> Exec['tuned-restart'] -> Exec['tuned-virtual-host']
}

exec {'tuned-virtual-host':
    unless => '/usr/sbin/tuned-adm active | /bin/grep virtual-host',
    command => '/usr/sbin/tuned-adm profile virtual-host',
    require => Service['tuned'],
}

