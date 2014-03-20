package{'python-cinderclient':
    before => Class["nova"]
}

nova_config{
    "DEFAULT/volume_api_class": value => "nova.volume.cinder.API";
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

exec {'tuned-virtual-host':
    unless => '/usr/sbin/tuned-adm active | /bin/grep virtual-host',
    command => '/usr/sbin/tuned-adm profile virtual-host',
    require => Service['tuned'],
}
